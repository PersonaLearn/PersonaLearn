import os
from typing import Any


class QueryTemplate:
    """Query template class to populate the training template with transcript information."""

    def __init__(self):
        self.cached_training_template = None

    def __read_training_template(self) -> str:
        """
        Read lines from the training template and return as a multi-line string.
        """
        # Load the training template if we don't have it already
        if self.cached_training_template is None:
            relative_template_path = "./training_template.txt"
            absolute_template_path = os.path.join(
                os.path.dirname(__file__), relative_template_path
            )
            with open(absolute_template_path, "r", encoding="utf-8") as file:
                # Filter lines if they start with #
                lines = [line for line in file if not line.startswith("#")]
                self.cached_training_template = "\n".join(lines)

        return self.cached_training_template

    def populate_template_with_variables(self, variables: dict[str, Any]) -> str:
        """
        Populate the training template with a set of variables.

        Variables in the training template begin with $ (for example, `$TEMPLATE_VARIABLE`).

        Returns a multi-line string with the relevant variables populated.
        """
        training_template = self.__read_training_template()

        for variable, value in variables.items():
            template_variable = f"${variable.upper()}"
            training_template = training_template.replace(template_variable, value)

        return training_template

    def generate_query(self, video_title: str, transcript: str) -> str:
        """Generate a GPT-3 query from a video title and transcript data."""
        return self.populate_template_with_variables(
            {
                "video_title": video_title,
                "transcript": transcript,
            }
        )
