# Copyright (c) 2021 DENSO WAVE INCORPORATED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: DENSO WAVE INCORPORATED

import os
import yaml
from ament_index_python.packages import get_package_share_directory
from launch.launch_context import LaunchContext
from launch.substitution import Substitution
from typing import Iterable, Text
from launch.some_substitutions_type import SomeSubstitutionsType


def load_yaml(package_name, file_path):
    """Load a YAML file from a ROS package share directory."""
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path) as file:
            return yaml.safe_load(file)
    except OSError:
        return None


class TextJoinSubstitution(Substitution):
    """Substitution that joins a namespace prefix with a fixed text string.

    Helpful for namespaces and/or MULTI-ROBOT applications.
    """

    def __init__(
            self, substitutions: Iterable[SomeSubstitutionsType], text: Text,
            sequence: Text) -> None:
        super().__init__()
        from launch.utilities import normalize_to_list_of_substitutions
        self.__substitutions = normalize_to_list_of_substitutions(substitutions)
        self.__text = text
        self.__sequence = sequence

    @property
    def substitutions(self) -> Iterable[Substitution]:
        return self.__substitutions

    def text(self) -> Text:
        return self.__text

    def describe(self) -> Text:
        return "LocalVar('{}')".format(" + ".join([s.describe() for s in self.substitutions]))

    def perform(self, context: LaunchContext) -> Text:
        performed_substitutions = [sub.perform(context) for sub in self.__substitutions]
        return self.__sequence.join(performed_substitutions) + self.__sequence + self.__text
