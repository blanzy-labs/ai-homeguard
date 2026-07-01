from app.models.questionnaire import (
    QuestionnaireAnswerType,
    QuestionnaireOption,
    QuestionnaireQuestion,
    QuestionnaireSection,
)

YES_NO_UNSURE = [
    QuestionnaireOption(value="yes", label="Yes"),
    QuestionnaireOption(value="no", label="No"),
    QuestionnaireOption(value="unsure", label="Not sure"),
]


def _question(
    question_id: str,
    section: str,
    prompt: str,
    options: list[QuestionnaireOption],
    help_text: str | None = None,
    required: bool = False,
    home_user_label: str | None = None,
) -> QuestionnaireQuestion:
    return QuestionnaireQuestion(
        id=question_id,
        section=section,
        prompt=prompt,
        help_text=help_text,
        answer_type=QuestionnaireAnswerType.SINGLE_CHOICE,
        options=options,
        required=required,
        home_user_label=home_user_label,
    )


QUESTIONNAIRE_SECTIONS = [
    QuestionnaireSection(
        id="router_wifi",
        title="Router and Wi-Fi",
        description="A few basics about the device that runs your home Wi-Fi.",
        questions=[
            _question(
                "router_admin_password_changed",
                "router_wifi",
                "Have you changed the router admin password from the default?",
                YES_NO_UNSURE,
                "This is the sign-in used to change router settings, not the code people use to join Wi-Fi.",
                required=True,
                home_user_label="Router admin password",
            ),
            _question(
                "wifi_wpa2_wpa3",
                "router_wifi",
                "Is your Wi-Fi protected with WPA2 or WPA3?",
                YES_NO_UNSURE,
                "Most modern routers show this as WPA2, WPA3, or WPA2/WPA3 in Wi-Fi security settings.",
                home_user_label="Wi-Fi protection",
            ),
            _question(
                "guest_wifi_available",
                "router_wifi",
                "Do you have a guest Wi-Fi network for visitors or smart devices?",
                YES_NO_UNSURE,
                "Guest Wi-Fi can keep visitors and less-trusted smart devices separate from personal computers.",
                home_user_label="Guest Wi-Fi",
            ),
            _question(
                "router_remote_admin_disabled",
                "router_wifi",
                "Is remote administration disabled on your router?",
                YES_NO_UNSURE,
                "Remote administration lets router settings be changed from outside your home. Most homes do not need it.",
                home_user_label="Remote router administration",
            ),
            _question(
                "router_firmware_updated",
                "router_wifi",
                "Do you know when your router firmware was last updated?",
                [
                    QuestionnaireOption(value="recently", label="Recently"),
                    QuestionnaireOption(value="over_6_months", label="Over 6 months ago"),
                    QuestionnaireOption(value="unsure", label="Not sure"),
                ],
                "Firmware updates are software updates for the router itself.",
                home_user_label="Router firmware",
            ),
        ],
    ),
    QuestionnaireSection(
        id="accounts_passwords",
        title="Accounts and passwords",
        description="Everyday account habits that help protect important services.",
        questions=[
            _question(
                "uses_password_manager",
                "accounts_passwords",
                "Do you use a password manager?",
                YES_NO_UNSURE,
                "A password manager helps create and remember unique passwords.",
                home_user_label="Password manager",
            ),
            _question(
                "uses_mfa_important_accounts",
                "accounts_passwords",
                "Do you use multi-factor authentication on important accounts?",
                [
                    QuestionnaireOption(value="yes", label="Yes"),
                    QuestionnaireOption(value="some", label="Some accounts"),
                    QuestionnaireOption(value="no", label="No"),
                    QuestionnaireOption(value="unsure", label="Not sure"),
                ],
                "Important accounts usually include email, banking, Apple, Google, Microsoft, and password managers.",
                required=True,
                home_user_label="Multi-factor authentication",
            ),
            _question(
                "separate_family_device_accounts",
                "accounts_passwords",
                "Do different family members use separate device accounts?",
                YES_NO_UNSURE,
                "Separate accounts can help keep settings, files, and parental controls clearer.",
                home_user_label="Separate device accounts",
            ),
        ],
    ),
    QuestionnaireSection(
        id="devices_updates",
        title="Devices and updates",
        description="How comfortable you feel about updates and connected devices.",
        questions=[
            _question(
                "regular_updates",
                "devices_updates",
                "Do you regularly install updates on computers and phones?",
                [
                    QuestionnaireOption(value="yes", label="Yes"),
                    QuestionnaireOption(value="sometimes", label="Sometimes"),
                    QuestionnaireOption(value="no", label="No"),
                    QuestionnaireOption(value="unsure", label="Not sure"),
                ],
                "Updates often include reliability fixes and security improvements.",
                home_user_label="Device updates",
            ),
            _question(
                "old_unsupported_devices",
                "devices_updates",
                "Do you still have old devices connected that no longer receive updates?",
                [
                    QuestionnaireOption(value="no", label="No"),
                    QuestionnaireOption(value="yes", label="Yes"),
                    QuestionnaireOption(value="unsure", label="Not sure"),
                ],
                "This can include old phones, tablets, laptops, cameras, or smart devices.",
                home_user_label="Old unsupported devices",
            ),
            _question(
                "knows_connected_devices",
                "devices_updates",
                "Do you know which devices are connected to your home network?",
                [
                    QuestionnaireOption(value="yes", label="Yes"),
                    QuestionnaireOption(value="mostly", label="Mostly"),
                    QuestionnaireOption(value="no", label="No"),
                    QuestionnaireOption(value="unsure", label="Not sure"),
                ],
                "A rough household device list is enough. Do not enter device identifiers here.",
                home_user_label="Connected devices",
            ),
        ],
    ),
    QuestionnaireSection(
        id="backups_recovery",
        title="Backups and recovery",
        description="Simple checks that help you recover important files if something goes wrong.",
        questions=[
            _question(
                "has_important_file_backups",
                "backups_recovery",
                "Do you have backups for important files?",
                YES_NO_UNSURE,
                "Think about photos, documents, school files, tax records, or anything hard to replace.",
                required=True,
                home_user_label="Important file backups",
            ),
            _question(
                "tested_backup_restore",
                "backups_recovery",
                "Have you tested restoring from backup?",
                YES_NO_UNSURE,
                "Testing one harmless file is enough to know the backup can actually be used.",
                home_user_label="Backup restore test",
            ),
            _question(
                "backup_separate_location",
                "backups_recovery",
                "Are important files backed up somewhere other than the same computer?",
                YES_NO_UNSURE,
                "Examples include an external drive kept separately or a reputable cloud backup service.",
                home_user_label="Separate backup location",
            ),
        ],
    ),
    QuestionnaireSection(
        id="smart_devices_family",
        title="Smart devices and family safety",
        description="Home devices and shared-device settings, without collecting personal details.",
        questions=[
            _question(
                "has_smart_devices",
                "smart_devices_family",
                "Do you have smart TVs, cameras, doorbells, speakers, or other IoT devices?",
                YES_NO_UNSURE,
                "Smart home devices can be useful, but they are worth keeping track of.",
                home_user_label="Smart devices",
            ),
            _question(
                "smart_devices_isolated",
                "smart_devices_family",
                "Are smart devices separated on guest Wi-Fi or another network?",
                [
                    QuestionnaireOption(value="yes", label="Yes"),
                    QuestionnaireOption(value="no", label="No"),
                    QuestionnaireOption(value="unsure", label="Not sure"),
                    QuestionnaireOption(value="not_applicable", label="Not applicable"),
                ],
                "This is optional, but it can be helpful for cameras, doorbells, and other connected devices.",
                home_user_label="Smart device separation",
            ),
            _question(
                "shared_family_devices",
                "smart_devices_family",
                "Do children or family members use shared devices?",
                YES_NO_UNSURE,
                "Shared devices can benefit from clear accounts, updates, and content settings.",
                home_user_label="Shared family devices",
            ),
            _question(
                "parental_controls_used",
                "smart_devices_family",
                "Are parental controls or content restrictions used where appropriate?",
                [
                    QuestionnaireOption(value="yes", label="Yes"),
                    QuestionnaireOption(value="no", label="No"),
                    QuestionnaireOption(value="unsure", label="Not sure"),
                    QuestionnaireOption(value="not_applicable", label="Not applicable"),
                ],
                "This can mean device settings, app store settings, streaming profiles, or router controls.",
                home_user_label="Family safety controls",
            ),
        ],
    ),
]


def get_questionnaire_sections() -> list[QuestionnaireSection]:
    return QUESTIONNAIRE_SECTIONS
