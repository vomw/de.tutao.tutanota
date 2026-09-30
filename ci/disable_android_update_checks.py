#!/usr/bin/env python3
"""Remove Android's proactive application-update prompt in CI build checkouts.

The server can still reject an incompatible client version. That enforcement is
intentionally retained because disabling it would leave normal API operations
unable to complete on an unsupported protocol version.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

POST_LOGIN_ACTIONS = Path("src/applications/common/login/PostLoginActions.ts")
APP_LOCATORS = (
    Path("src/applications/mail-app/mailLocator.ts"),
    Path("src/applications/calendar-app/calendarLocator.ts"),
    Path("src/applications/drive-app/driveLocator.ts"),
)

RECEIVE_INFO_IMPORT = (
    'import { createReceiveInfoServiceData, OutOfOfficeNotification, ReceiveInfoService_POST } from "@tutao/entities/tutanota"'
)
OUT_OF_OFFICE_IMPORT = 'import { OutOfOfficeNotification } from "@tutao/entities/tutanota"'

UPDATE_CLIENT_PARAMETER = "\t\tprivate readonly updateClient: () => unknown,\n"
UPDATE_CHECK_BLOCK = """\t\tif (this.logins.isGlobalAdminUserLoggedIn() && !EnvProvider.get().isAdminClient()) {
\t\t\tconst receiveInfoData = createReceiveInfoServiceData({
\t\t\t\tlanguage: lang.code,
\t\t\t})
\t\t\tconst receiveInfoServicePostOut = await locator.serviceExecutor.execute(ReceiveInfoService_POST, receiveInfoData, null)
\t\t\tif (receiveInfoServicePostOut && receiveInfoServicePostOut.outdatedVersion) {
\t\t\t\treturn Dialog.updateReminder(true, () => {
\t\t\t\t\tthis.updateClient()
\t\t\t\t})
\t\t\t}
\t\t}

"""
LOCATOR_UPDATE_CLIENT_ARGUMENT = "\t\t\t() => this.showSetupWizard(),\n\t\t\t() => this.updateClients(),\n\t\t\tthis.loginFacade,"
LOCATOR_WITHOUT_UPDATE_CLIENT_ARGUMENT = "\t\t\t() => this.showSetupWizard(),\n\t\t\tthis.loginFacade,"


def verify_once(path: Path, old: str) -> None:
    content = path.read_text(encoding="utf-8")
    occurrences = content.count(old)
    if occurrences != 1:
        raise RuntimeError(f"Expected one matching block in {path}, found {occurrences}")


def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    patches = [
        (ROOT / POST_LOGIN_ACTIONS, RECEIVE_INFO_IMPORT, OUT_OF_OFFICE_IMPORT),
        (ROOT / POST_LOGIN_ACTIONS, UPDATE_CLIENT_PARAMETER, ""),
        (ROOT / POST_LOGIN_ACTIONS, UPDATE_CHECK_BLOCK, ""),
        *(
            (ROOT / locator, LOCATOR_UPDATE_CLIENT_ARGUMENT, LOCATOR_WITHOUT_UPDATE_CLIENT_ARGUMENT)
            for locator in APP_LOCATORS
        ),
    ]

    for path, old, _ in patches:
        verify_once(path, old)

    if sys.argv[1:] == ["--check"]:
        print("Android update-check patch inputs verified.")
        return 0
    if sys.argv[1:]:
        raise RuntimeError("Usage: disable_android_update_checks.py [--check]")

    for path, old, new in patches:
        replace_once(path, old, new)

    print("Disabled the Android build's proactive app-update check.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"Update-check patch failed: {error}", file=sys.stderr)
        raise SystemExit(1)
