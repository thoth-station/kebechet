"""AI powered labels for all your issues."""

import logging
from kebechet.managers.manager import ManagerBase
import typing
import os
import requests
import json

_LOGGER = logging.getLogger(__name__)

# Github and Gitlab events on which the manager acts upon.
_EVENTS_SUPPORTED = ["issues", "issue"]

_GITHUB_LABEL_BOT_API = os.getenv("LABELBOT_URL")
_MINIMUM_CONFIDENCE = 0.5
_ISSUES_TO_IGNORE = [
    "Kebechet",
    "new patch release",
    "new minor release",
    "new major release",
    "new calendar release",
    "new pre-release",
    "new build release",
]


class ThothLabelBotManager(ManagerBase):
    """Labels issue using Thoth Github Issue classifier."""

    def assign_label(self, response_dict: dict) -> typing.Tuple[typing.Any, float]:
        """Return the label with the highest confidence in the response."""
        label_confidence = []
        for key in response_dict.keys():
            if key not in ["title", "body"]:
                label_confidence.append((key, float(response_dict[key])))
        label_confidence.sort(key=lambda x: x[1], reverse=True)
        return label_confidence[0]

    def run(self) -> typing.Optional[dict]:  # type: ignore
        """Check for info issue and close it with a report."""
        if self.parsed_payload:
            if self.parsed_payload.get("event") not in _EVENTS_SUPPORTED:
                _LOGGER.info(
                    "Label manager doesn't act on %r events.",
                    self.parsed_payload.get("event"),
                )
                return None
            # Note this manager is currently only supported on Github.
            if (
                self.parsed_payload.get("service_type") != "github"
                or _GITHUB_LABEL_BOT_API is None
            ):
                _LOGGER.info("Label manager doesn't act on non github services.")
                return None

        payload = self.parsed_payload.get("raw_payload").get("payload")  # type: ignore
        if payload.get("action") == "opened":
            issue_title = payload.get("issue").get("title")
            issue = self.sm.get_issue(issue_title)
            if not issue:
                _LOGGER.info("Issue not found, exiting")
                return None

            # TODO: Read from thoth.yaml so that user could add more issues to ignore.
            for issue_to_ignore in _ISSUES_TO_IGNORE:
                if issue_title.startswith(issue_to_ignore):
                    _LOGGER.info("Ignored as it is a BOT related issue.")
                    return None

            _LOGGER.info(f"Found issue {issue_title}, predicting label.")
            url = _GITHUB_LABEL_BOT_API + "/predict"  # type: ignore
            headers = {"Content-type": "application/json", "Accept": "text/plain"}
            data = {"title": str(issue.title), "body": str(issue.description)}
            response = requests.request(
                "POST", url, headers=headers, data=json.dumps(data)
            )
            if response.status_code == 200:
                response_dict = response.json()
                label, confidence = self.assign_label(response_dict)
                if confidence > _MINIMUM_CONFIDENCE:
                    issue.comment(
                        f"Kebechet predicts this issue to be of type: {label} with confidence: {confidence}"
                    )
                    issue.add_label(label)
                # Ignore if the none of the label meet the minimum confidence criteria.
            else:
                _LOGGER.warning("Github Label BOT API is not working.")

        return None
