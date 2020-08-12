# neptune-action

This repo contains code used in the article [How to set up Continuous Integration for Machine Learning with Github Actions and Neptune]()

# What it is?

It is an example project with continous integration worfkflow for machine learning set up with Github Actions and Neptune.
The CI workflow works in the following way:

* on each Pull Request from branch develop to master
* run model training on branch develop
* run model training on branch master
* create a run comparison markdown table showing diffs and links to Neptune experiments
* post a comment on the Pull Request with a table and links

![image](https://neptune.ai/wp-content/uploads/pr_comment.gif)

Check out the [Pull Request](https://github.com/neptune-ai/neptune-action/pull/31) live. 

# How to use it?

## Fork the repository and create a PR

You can simply form this repository, and create a PR from branch develop to master and see how the CI is working.

## Copy the `neptune_action.yml` to your project

To set up CI for your project you can just copy the [`neptune_action.yml`](https://github.com/neptune-ai/neptune-action/blob/master/.github/workflows/neptune_action.yml) to the `.github/workflows` directory and adjust it if needed.
