# Privacy Policy

Publication Date: 29 March 2026

## Privacy Policy for firestorm-discord-bot

This Privacy Policy describes what information is collected, used, and shared by the firestorm-discord-bot.

### How Information is Collected and Used

There are two types of information collected and logged by this bot:

1) Server Information:
    - This bot stores the following information, related to servers:
        - A list of server IDs that are allowlisted by this bot,
        - A list of server IDs that have invited this bot.
        - A list of roles. This is not specific to the guild itself, but a generic list of roles.
    - Note that server IDs are also known as guild IDs in discord terminology.
    - Server IDs are solely used to check that the invited bot has been allowlisted, before the bot allows its commands to be run on that specific server.
    - The list of roles is used to check against user roles when users run certain slash commands. This is used to ensure that only specific roles can run these commands.
    - This information will also be logged and only used to debug problems related to spurious network errors or inability to provide its services.

2) Message Content:
    - When a user runs slash commands provided by this bot, only information that is related to the dataset will be stored. No personal identifying user information is logged nor stored.
    - The following information from the message content will be stored. Depending on which slash command is run, some of the following information will be stored:
        - Pool Name (ie, dataset name)
        - Prompt
        - Sensitivity (ie. the Prompt Rating level)
        - Weight (ie. how often this prompt should be picked over other prompts)
        - Flags (ie. additional tags related to this prompt)
        - Approved (ie. whether this prompt has been approved yet or pending approval)
        - Rejected (ie. whether this prompt has been rejected)
        - Rejection Reason (ie. If the prompt was rejected, the reason for rejection)
    - Errors that occur will be logged and only used for debugging the service and improving it.

### Data Retention

Logs are only retained for as long as necessary to provide services.

### Sharing of Data
The data stored by this dataset can be synced with the [firestorm-bingo app](https://github.com/FireStormShipping/firestorm-bingo) via the `/sync-dataset` slash command, which performs all the necessary operations to make a Pull Request.