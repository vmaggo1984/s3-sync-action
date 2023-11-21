from typing import Literal, Union
from cookiecutter.main import cookiecutter
from pydantic import Field, root_validator
from os import environ, path


def create_api(context: dict):

    extra_context = {**context}
    print(extra_context)

    cookiecutter(
        template=path.dirname(__file__),
        directory=".",
        no_input=True,
        extra_context=extra_context["dag"],
        overwrite_if_exists=True,
        output_dir=".",
    )


def main(context: Union[dict, None] = None):
    if context:
        create_api(context)


if __name__ == "__main__":
    context = dict(
        dag=dict(
            baz_type=environ.get("BAZ_TYPE"),
            domain_area=environ.get("DOMAIN_AREA"),
            analytics_area=environ.get("ANALYTICS_AREA"),
            srm_tier=environ.get("SRM_TIER"),
            snowflake_account=environ.get("SNOWFLAKE_ACCOUNT"),
            working_directory="python/testapi-{}.py".format(
                environ.get("DOMAIN_AREA")
            )
        )
    )
    main(context)
