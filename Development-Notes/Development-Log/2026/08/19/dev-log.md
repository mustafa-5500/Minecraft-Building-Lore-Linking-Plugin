**Date:** 2026-08-19
Previous Entry: [2026-08-05](../05/dev-log.md)

**Developer:**
    - Mustafa Faheem
    - Almond (Mustafa)

**Comments:**
We moved the [Utils](../../Utils/) folder to its own git repository, since the scripts warranted their own features and git history, which would not make sense or be organized if they were added in the plugin repository.

We also improved the dev log format to include a **Goal** and **Action:** section to help track what we want to accomplish, and how we are accomplishing that. Also moved the logs outside of the [Inidividual Logs](../Individual%20Log/) folders, so that the [Development Logs](../Development%20Log/) are used by every developer working on the project, to help communicate between developers and between different development time periods about what is happening.

Perhaps we should make it 3 layers of folders, `[year]/[month]/[day]/` then each markdown becomes a `dev-log.md` file, and if there are other files such as pictures we might want, we can find them. This also make it so that we can just do `cd /[year]/[month]/[day]/` or open the dev log corresponding the a specific day, while simultaneously maintaining a cleaner directory and dev-log names and paths.

We should probably add some sort of script which will automatically generate a template dev-log and put it in the right location, to help reduce the organization work to maintain the dev log, and therefore encourage developers to use it.

**Goal:**
    - ~~Make [Utils](../../Utils/) a submodule.~~
    - ~~Improve the development logging/organizing~~

**Action:**
    - ~~Move the [Utils](../../Utils/) folder into its own repository and convert it into a submodule for this repository.~~
    - ~~Split out the [Development Log](../Development%20Log/) from the [Inidividual Log](../Individual%20Log/).~~
    - ~~Rename the parent folder [Development](../../Development/) into something more meaningful, such as `Development-Notes` to make its use/functionality more known.~~
    - ~~Add a **Developer:** and **Comments:** section to the note to make it more usable and track the developer(s) working, so if the writing is not clear enough, the last developer can be contacted.~~
    - ~~Move daily notes into Month specific subfolder, to reduce clutter while maintaining the history.~~
    - ~~Adjust the [commit hook](../../../../../.git/hooks/pre-commit) to the new folder structure of [Development-Notes](../../../../../Development-Notes/)~~
    - ~~Create a script to generate a template for the day's dev-log, if it does not exist, otherwise open the day's dev-log for the developer.~~
    