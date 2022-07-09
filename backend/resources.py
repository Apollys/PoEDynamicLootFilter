import os.path

import consts
import file_helper

# List of all Flask BaseTypes
kFlaskBaseTypesTxtFilepath = os.path.join(consts.kResourcesDirectory, 'flask_base_types.txt')
kAllFlaskTypes = file_helper.ReadFile(kFlaskBaseTypesTxtFilepath, strip=True)