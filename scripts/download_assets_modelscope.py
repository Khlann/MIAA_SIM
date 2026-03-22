import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse


def run(cmd, cwd=None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download MIAA_SIM assets from ModelScope dataset repo into local ./asset."
    )
    parser.add_argument(
        "--namespace",
        default="arlenkang",
        help="ModelScope dataset owner/namespace (default: arlenkang).",
    )
    parser.add_argument(
        "--dataset",
        default="MIAA_SIM",
        help="ModelScope dataset name (default: MIAA_SIM).",
    )
    parser.add_argument(
        "--local-dir",
        default=".",
        help="Where to place downloaded files (default: current directory).",
    )
    parser.add_argument(
        "--clone-url",
        default=None,
        help=(
            "If provided, use this full git clone URL directly "
            "(e.g. https://www.modelscope.cn/datasets/owner/name.git)."
        ),
    )
    parser.add_argument(
        "--git-token",
        default=None,
        help=(
            "Optional token for private repos. If set and --clone-url is not provided, "
            "we will try to embed it into the clone URL using an oauth2 form."
        ),
    )
    parser.add_argument(
        "--repo-base",
        default="https://www.modelscope.cn/datasets",
        help="ModelScope dataset repo base URL (default matches modelscope website).",
    )
    args = parser.parse_args()

    local_dir = Path(args.local_dir).resolve()
    local_asset_dir = local_dir / "asset"

    if args.clone_url:
        clone_url = args.clone_url
    else:
        if args.git_token:
            # Common pattern for private git access:
            #   https://oauth2:TOKEN@host/<path>.git
            parsed = urlparse(args.repo_base)
            if not parsed.scheme or not parsed.netloc:
                raise SystemExit(f"Invalid --repo-base: {args.repo_base}")
            base_path = parsed.path.rstrip("/")
            clone_url = f"{parsed.scheme}://oauth2:{args.git_token}@{parsed.netloc}{base_path}/{args.namespace}/{args.dataset}.git"
        else:
            clone_url = f"{args.repo_base}/{args.namespace}/{args.dataset}.git"

    tmp_dir = Path(tempfile.mkdtemp(prefix="miaa_sim_modelscope_"))
    repo_dir = tmp_dir / "repo"
    try:
        print(f"Cloning ModelScope dataset via git-lfs: {clone_url}")
        run(["git", "lfs", "install"])
        run(["git", "clone", clone_url, str(repo_dir)])

        remote_asset_dir = repo_dir / "asset"
        if not remote_asset_dir.exists():
            raise SystemExit(
                f"Downloaded repo does not contain 'asset/' at {remote_asset_dir}. "
                "Please check dataset structure."
            )

        # Replace local asset/ to match the downloaded one.
        if local_asset_dir.exists():
            shutil.rmtree(local_asset_dir)
        shutil.copytree(remote_asset_dir, local_asset_dir)
        print(f"Assets downloaded to: {local_asset_dir}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()

