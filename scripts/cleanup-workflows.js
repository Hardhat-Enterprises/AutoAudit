import { Octokit } from "@octokit/rest";

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = process.env.REPO_OWNER;
const REPO_NAME = process.env.REPO_NAME;

const args = process.argv.slice(2);
const isDryRun = args.includes("--dryRun=true");

if (!GITHUB_TOKEN || !REPO_OWNER || !REPO_NAME) {
  console.error("❌ Missing environment variables (GITHUB_TOKEN, REPO_OWNER, REPO_NAME)");
  process.exit(1);
}

const octokit = new Octokit({ auth: GITHUB_TOKEN });

async function cleanupWorkflows() {
  console.log(`🔎 Checking workflow runs for ${REPO_OWNER}/${REPO_NAME}...`);

  try {
    const { data } = await octokit.actions.listWorkflowRunsForRepo({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      per_page: 20,
    });

    if (data.workflow_runs.length === 0) {
      console.log("ℹ️ No workflow runs found.");
      return;
    }

    for (const run of data.workflow_runs) {
      let durationSec = "unknown";
      if (run.run_started_at && run.updated_at) {
        const start = new Date(run.run_started_at);
        const end = new Date(run.updated_at);
        durationSec = Math.round((end - start) / 1000);
      }

      // Default action = KEEP
      let decision = "✅ KEEP";

      //SETTING UP THE RULES 
      if (durationSec !== "unknown") {
        if (durationSec < 10) {
          decision = "🗑️ DELETE (<10s)";
        } else if (durationSec >= 120) {
          decision = "✅ KEEP (>2min)";
        } else {
          decision = "🗑️ DELETE (10s–2min)";
        }
      }

      if (isDryRun) {
        console.log(
          `• Run #${run.id} | Name: ${run.name} | Duration: ${durationSec}s | Status: ${decision}`
        );
      } else if (decision.startsWith("🗑️ DELETE")) {
        await octokit.actions.deleteWorkflowRun({
          owner: REPO_OWNER,
          repo: REPO_NAME,
          run_id: run.id,
        });
        console.log(`🗑️ Deleted workflow run #${run.id} (${durationSec}s)`);
      }
    }

    if (isDryRun) {
      console.log("\n⚠️ Dry run complete. No workflows were deleted.");
    }
  } catch (err) {
    console.error("❌ Error while cleaning workflows:", err.message);
  }
}

cleanupWorkflows();
