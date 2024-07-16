import asyncio
import json
import os
import os.path
import re
import sys

import aiohttp

from packaging.version import Version

NATIVE_ARCHS = ('32', '64')
KNOWN_FEATURES = (
    'is_demo_user',
    'has_custom_resolution',
    'has_quick_plays_support',
    'is_quick_play_singleplayer',
    'is_quick_play_multiplayer',
    'is_quick_play_realms',
)
KNOWN_VARIABLES = (
    'auth_username',
    'auth_session',
    'auth_access_token',
    'auth_player_name',
    'auth_uuid',
    'profile_name',
    'version_name',
    'version_type',
    'game_directory',
    'natives_directory',
    'classpath',
    'resolution_width',
    'resolution_height',
    'game_assets',
    'assets_root',
    'assets_index_name',
    'user_type',
    'user_properties',
    'launcher_name',
    'launcher_version',
    # These are ignored because they rely on features that are disabled:
    'quickPlayPath',
    'quickPlaySingleplayer',
    'quickPlayMultiplayer',
    'quickPlayRealms',
    # These are not handled yet, but they don't cause issues:
    'clientid',
    'auth_xuid',
)

SUBSTITUTION_REGEX = re.compile(r'\$\{([^}]+)\}')

def process_version(v):
    assert v.get('minimumLauncherVersion', 0) <= 21

    natives_detected = False

    if 'downloads' in v:
        v['downloads'] = {k: v for k, v in v['downloads'].items() if k == 'client'}

    #if 'assets' in v:
    #    del v['assets']

    libs = []
    for lib in v['libraries']:
        if 'downloads' in lib:
            if 'artifact' in lib['downloads']:
                if 'path' in lib['downloads']['artifact']:
                    del lib['downloads']['artifact']['path']
            #if 'classifiers' in lib['downloads']:
            #    if 'javadoc' in lib['downloads']['classifiers']:
            #        del lib['downloads']['classifiers']['javadoc']
            #    if 'sources' in lib['downloads']['classifiers']:
            #        del lib['downloads']['classifiers']['sources']
            if 'natives' in lib:
                native_keys = []

                natives_detected = True

                # Process native keys for ${arch} values
                for native_key in lib['natives'].values():
                    if '${arch}' in native_key:
                        for native_arch in NATIVE_ARCHS:
                            native_keys.append(native_key.replace('${arch}', native_arch))
                    else:
                        native_keys.append(native_key)

                # Remove any classifiers that are not in the natives key (unused natives/classifiers)
                lib['downloads']['classifiers'] = {k: v for k, v in lib['downloads']['classifiers'].items() if k in native_keys}
        libs.append(lib)

    v['libraries'] = libs

    if 'logging' in v:
        del v['logging']

    if 'complianceLevel' in v:
        del v['complianceLevel']

    if 'javaVersion' not in v:
        v['javaVersion'] = {'component': 'jre-legacy', 'majorVersion': 8}

    # Warn if natives are missing, for MC versions older than 1.19
    if not natives_detected and Version(v['id']) < Version('1.19'):
        print('[!!] Warning: No natives detected')

    has_feature_errors = False
    has_variable_errors = False

    game_arguments = v.get('arguments', {}).get('game')
    if game_arguments:
        for argument in game_arguments:
            # Check substitution variables
            if isinstance(argument, str):
                variables_used = SUBSTITUTION_REGEX.findall(argument)
                for variable_used in variables_used:
                    if variable_used not in KNOWN_VARIABLES:
                        print(f'[!!] Error: Unknown variable {variable_used} in argument {argument}')
                        has_variable_errors = True

            # Check unknown features and variables within rules
            if isinstance(argument, dict) and 'rules' in argument:
                for rule in argument['rules']:
                    for feature in rule['features'].keys():
                        if feature not in KNOWN_FEATURES:
                            print(f'[!!] ERROR: Unknown feature {feature} in argument {argument}')
                            has_feature_errors = True
                for value in argument.get('value', []):
                    variables_used = SUBSTITUTION_REGEX.findall(value)
                    for variable_used in variables_used:
                        if variable_used not in KNOWN_VARIABLES:
                            print(f'[!!] Error: Unknown variable {variable_used} in argument {argument!r}')
                            has_variable_errors = True

    if has_feature_errors:
        print('Aborting due to rule feature errors')
        sys.exit(1)

    if has_variable_errors:
        print('Aborting due to variable errors')
        sys.exit(1)

    return v

async def main():
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        print('Fetching versions')

        async with session.get('https://launchermeta.mojang.com/mc/game/version_manifest_v2.json') as resp:
            mcs = await resp.json()

        changed = []
        new = []

        for mc in mcs['versions']:
            if mc['type'] != 'release' and mc['id'] != '1.5':  # For some reason we have 1.5 at Technic, even tho it's a snapshot
                # print(f'Skipping {mc["id"]}, type {mc["type"]}')
                continue

            version = mc['id']

            print(f'Processing {version}')

            async with session.get(mc['url']) as resp:
                j = await resp.json()

            target = os.path.join('version', version, version + '.json')

            target_dir = os.path.dirname(target)

            if not os.path.exists(target_dir):
                print(f'Making dir {target_dir}')
                os.mkdir(target_dir)
                new.append(version)

            j = process_version(j)
            new_json = json.dumps(j, separators=(', ', ': '))

            # This is to minimize writes, so it doesn't waste writes on my SSD when
            # no changes actually happen
            if os.path.exists(target):
                with open(target, 'r', encoding='utf-8') as f:
                    old_json = f.read()

                if old_json == new_json:  # if old == new
                    print('Version file is the same we already have, skipping')
                    continue

            with open(target, 'w', encoding='utf-8') as f:
                f.write(new_json)

            if version not in new:
                changed.append(version)

    if changed:
        print('Updated versions: ' + ', '.join(changed))
    else:
        print('No updated versions')

    if new:
        print('New versions: ' + ', '.join(new))
    else:
        print('No new versions')

asyncio.run(main())
