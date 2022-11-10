"""A script for updating the JSON file controlling the version switching."""

import argparse
import json


def sort_versions_descending(versions_list):
    """Sort a list of semantic versions in descending order.

    Parameters
    ----------
    versions_list : list[str]
        A list of strings containing the semantic versions to be sorted.

    """
    versions_list.sort(key=lambda semver: [int(digit) for digit in semver.split(".")])
    return versions_list[::-1]


def update_switch_version_file(filename, new_version, cname, render_last):
    """Add new version number and associated URL to JSON file.

    Parameters
    ----------
    filename : str
        File name of the version switcher JSON file.
    new_version : str
        The new version to be added to the version switcher JSON file.
    cname : str
        The canonical name of the project's documentation website.
    render_last : int
        The number of stable releases to be shown in the version switcher.

    """
    with open(f"release/{filename}", "r") as switcher_file:
        # Load the content of the
        current_content = json.load(switcher_file)

        # Collect all the version numbers in the JSON file
        current_raw_versions_list = [
            data["version"] for data in current_content if data["version"] != "dev"
        ]

        # Remove the "(stable)" label to retain only version numbers
        current_versions_list = []
        for version in current_raw_versions_list:
            if version.endswith(" (stable)"):
                current_versions_list.append(version[: -len(" (stable)")])
            else:
                current_versions_list.append(version)

        # Verify if new version is alerady registered in the JSON file
        new_version_exists = new_version in current_versions_list
        if not new_version_exists:
            current_versions_list.append(new_version)

        # Sort all current versions in descending order
        current_versions_list = sort_versions_descending(current_versions_list)

        # Select only the desired number of versions
        if len(current_versions_list) > render_last:
            new_versions_list = current_versions_list[:render_last]
        else:
            new_versions_list = current_versions_list

        # Force the HTTPS in front of the CNAME
        cname = f"https://{cname}" if not cname.startswith("https://") else cname

        # Generate the new content
        new_content = []

        # The first data for the new content is always the development version
        new_content.append(dict(version="dev", url=cname))

        # Append the information for the new content
        for ith_version, version in enumerate(new_versions_list):
            version_name = f"{version} (stable)" if ith_version == 0 else version
            new_data = dict(version=version_name, url=f"{cname}/release/{version}")
            new_content.append(new_data)

    # Override the whole content of the version switches JSON file with the new
    # generated version data
    with open(f"release/{filename}", "w") as switcher_file:
        # Update JSON file with the new content
        json.dump(new_content, switcher_file, indent=4)


def parse_cli_arguments():
    """Parse all command line arguments."""
    parser = argparse.ArgumentParser(description="Version switcher JSON file updater.")
    parser.add_argument(
        "-c", "--cname", type=str, help="Canonical name of the project's documentation."
    )
    parser.add_argument(
        "-f",
        "--json_filename",
        type=str,
        default="versions.json",
        help="Name of the JSON file controlling the version switch.",
    )
    parser.add_argument(
        "-n",
        "--new_version",
        type=str,
        help="Semantic version to be added to the version switcher.",
    )
    parser.add_argument(
        "-r",
        "--render_last",
        type=int,
        default=3,
        help="Number of latest stable versions to be included in the project's documentation.",
    )
    return parser.parse_args()


def main():
    """Entry function of the script."""
    # Parse all command line arguments
    args = parse_cli_arguments()

    # Update the version swithcher JSON file with desired information
    update_switch_version_file(
        args.json_filename, args.new_version, args.cname, args.render_last
    )


if __name__ == "__main__":
    main()