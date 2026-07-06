import { redirect } from "next/navigation";
import WorkspacePage from "./workspace/page";

const wwwWorkspaceBuild = process.env.NF_WWW_WORKSPACE_BUILD === "1";

export default function HomePage() {
  if (wwwWorkspaceBuild) {
    return <WorkspacePage />;
  }
  redirect("/cognitive-dashboard");
}
