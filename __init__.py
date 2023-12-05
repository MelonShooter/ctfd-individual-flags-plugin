from flask import Blueprint

from CTFd.models import Challenges, Flags, db
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.flags import FlagException, get_flag_class
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.migrations import upgrade
from CTFd.utils.user import get_current_user

import re
import hashlib
import hmac

PLUGIN_NAME = "ctfd-individual-flags-plugin"
CHALLENGE_NAME = "individual"


class IndividualChallengeModel(Challenges):
    __mapper_args__ = {"polymorphic_identity": CHALLENGE_NAME}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    hmackey = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(IndividualChallengeModel, self).__init__(**kwargs)


class IndividualChallenge(BaseChallenge):
    id = CHALLENGE_NAME
    name = CHALLENGE_NAME
    templates = (
        {
            "create": f"/plugins/{ PLUGIN_NAME }/assets/create.html",
            "update": f"/plugins/{ PLUGIN_NAME }/assets/update.html",
            "view": f"/plugins/{ PLUGIN_NAME }/assets/view.html",
        }
    )
    scripts = {
        "create": f"/plugins/{ PLUGIN_NAME }/assets/create.js",
        "update": f"/plugins/{ PLUGIN_NAME }/assets/update.js",
        "view": f"/plugins/{ PLUGIN_NAME }/assets/view.js",
    }
    route = f"/plugins/{ PLUGIN_NAME }/assets/"
    blueprint = Blueprint(
        PLUGIN_NAME,
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = IndividualChallengeModel

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = IndividualChallengeModel.query.filter_by(
            id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "hmackey": challenge.hmackey,
            "description": challenge.description,
            "connection_info": challenge.connection_info,
            "next_id": challenge.next_id,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def attempt(cls, challenge, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()

        for flag in flags:
            try:
                # Only works if the flag is static.
                if flag.type != "static":
                    raise FlagException(
                        f"Only static flags are allowed, found a \"{ flag.type }\" type flag. Contact an administrator with this error.")

                # Get correct flag.
                # TODO: Perform side-channel attack analysis on this.
                username = get_current_user().name
                unique_flag_part_len = re.search(
                    r"%%%%(\d)+%%%%", flag.content).group(1)
                unique_flag_part = hmac.new(bytes(challenge.hmackey), bytes(
                    username), hashlib.sha256).hexdigest()[:unique_flag_part_len]
                correct_flag = re.sub(
                    r"%%%%(\d)+%%%%", unique_flag_part, flag.content)

                # Compare flag.
                if len(correct_flag) != len(submission):
                    continue

                result = 0

                if flag.data == "case_insensitive":
                    for x, y in zip(correct_flag.lower(), submission.lower()):
                        result |= ord(x) ^ ord(y)
                else:
                    for x, y in zip(correct_flag, submission):
                        result |= ord(x) ^ ord(y)

                if result == 0:
                    return True, "Correct"
            except FlagException as e:
                return False, str(e)

        return False, "Incorrect"


def load(app):
    upgrade(plugin_name=PLUGIN_NAME)
    CHALLENGE_CLASSES[CHALLENGE_NAME] = IndividualChallenge
    register_plugin_assets_directory(
        app, base_path=f"/plugins/{ PLUGIN_NAME }/assets/")
