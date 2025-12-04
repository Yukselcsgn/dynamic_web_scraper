# Copyright 2024 Yüksel Coşgun
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

from random import uniform
from time import sleep


def sleep_random(min_time, max_time):
    """
    Rastgele bir süre bekler.

    Args:
        min_time (float): Minimum bekleme süresi (saniye).
        max_time (float): Maksimum bekleme süresi (saniye).

    Usage:
        sleep_random(2, 5)  # 2 ile 5 saniye arasında rastgele bekler.
    """
    wait_time = uniform(min_time, max_time)
    print(f"{wait_time:.2f} saniye bekleniyor...")
    sleep(wait_time)
