# llmops-issue-resolver

After an issue in the **toy-issues-with-github-actions repo** is labeled as *assigned-to-llmops-issue-resolver*, the **Github Action workflow lmops-issue-resolver** attached to the respective repo should run.

This Workflow uses the **Github Action lmops-issue-resolver** which lives in the **llmops-issue-resolver repo**.

When the Workflow finishes there should be a new PR addressing the issue, made by the **llmops-issue-resolver workflow**.

There is also a GH Action Workflow for publishing this package which lives in this repo. The package is built and published to Test PyPi on a push to the release branch. The package is built and published to PyPi on a tagged push to the release branch. The workflow uses the recent "Trsuted Publishers" PyPi Feature, where you don't need to worry about tokens, they are exchanged between PyPi and the trusted Publisher (Github in this case) under the hood.