from CTFd.plugins.challenges import CHALLENGE_CLASSES, CTFdStandardChallenge, BaseFlag
from CTFd.plugins.flags import FLAG_CLASSES, FlagException, get_flag_class, CTFdStaticFlag
from CTFd.models import Flags
from CTFd.plugins import register_plugin_assets_directory

CHALLENGE_NAME = "individual"
FLAG_NAME = "key"


class KeyFlag(BaseFlag):
    name = FLAG_NAME
    templates = {
        "create": "/plugins/individual_challenges/assets/keys/create.html",
        "update": "/plugins/individual_challenges/assets/keys/edit.html",
    }

    @staticmethod
    def compare(chal_key_obj, provided):
        return False


class IndividualChallenge(CTFdStandardChallenge):
    id = CHALLENGE_NAME
    name = CHALLENGE_NAME

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
                if flag.type == CTFdStaticFlag:
                    # use flag.content for what static flag is
                    # use submission for the flag submission
                    pass
                elif flag.type == KeyFlag:
                    pass
            except FlagException as e:
                return False, str(e)
        return False, "Incorrect"


def load(app):
    CHALLENGE_CLASSES[CHALLENGE_NAME] = IndividualChallenge
    FLAG_CLASSES[FLAG_NAME] = KeyFlag
    register_plugin_assets_directory(
        app, base_path="/plugins/individual_challenges/assets/keys/")
