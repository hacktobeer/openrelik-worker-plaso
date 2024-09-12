# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import subprocess
import os

def log2timeline_status_to_dict(status_string: str) -> dict:
    """Convert a log2timeline status string to a dictionary.

    Args:
        status_string: The status string to convert.

    Returns:
        A dictionary containing the status information.
    """
    result_dict = {"tasks": {}}
    items = status_string.split()[1:]

    for name, value in zip(items[::2], items[1::2]):
        result_dict["tasks"][name.strip(":").lower()] = int(value)

    return result_dict

def mount_input(input_files: list) -> list:
    """Mount GCE disk.

    Args:
        input_files: List of input files with GCE disk info.

    Returns:
        A input files path pointing to the mounted GCP disk path or the original input file list
    """
    if input_files[0].get("type") == "gce":
        hostname = os.environ.get('HOSTNAME')
        zone=_get_gce_zone()
        device_name="mydisk" # TODO plumb through artifact id

        command = [
            '/usr/bin/gcloud',
            'compute',
            'instances',
            'attach-disk',
            hostname,
            '--disk',
            input_files[0].get("path"),
            '--zone',
            zone,
            '--device-name='+device_name, 
            '--mode=ro',
        ]
        
        print("Mounting GCE disk")
        #print(command)
        subprocess.call(command)

        input_files[0]["path"] = "/dev/disk/by-id/google-"+device_name

    return input_files

def umount_input(input_files: list) -> None:
    """Umount GCE disk.

    Args:
        input_files: List of input files with GCE disk info.

    Returns:
        None
    """
    if input_files[0].get("type") == "gce":
        hostname = os.environ.get('HOSTNAME')
        zone=_get_gce_zone()

        command = [
            '/usr/bin/gcloud',
            'compute',
            'instances',
            'detach-disk',
            hostname,
            '--disk',
            input_files[0].get("path"),
            '--zone='+zone,
        ]

        subprocess.call(command)

def _get_gce_zone() -> str:
    # TODO this fails with a curl error... use gcloud to get zone!!
    # command = [
    #     '/usr/bin/curl',
    #     '-s',
    #     'http://metadata.google.internal/computeMetadata/v1/instance/zone',
    #     '-H',
    #     'Metadata-Flavor:Google',
    #     '|',
    #     'cut',
    #     '\'-d/\'',
    #     '-f4',
    # ]
    # print("DEBUG")
    # command_string = " ".join(command)
    # print(command_string)
    # zone = subprocess.check_output(command, shell=True).strip()
    zone="us-central1-b"

    return zone