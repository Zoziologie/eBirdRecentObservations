#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import List
import e2L  # single-file module

# Load environment variables from .env file
load_dotenv()


def fetch_region_info(region_code, api_key):
    """
    Fetch region information from eBird API.

    Args:
        region_code: The eBird region code (e.g., 'CH', 'FR-GES')
        api_key: eBird API key

    Returns:
        dict: Region information including name
    """
    url = f"https://api.ebird.org/v2/ref/region/info/{region_code}"
    headers = {"X-eBirdApiToken": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching region info for {region_code}: {e}")
        return None


def download_barchart(
    region_code,
    outdir="public/barchartData",
    force=False,
):
    """
    Download eBird bar chart data and save as JSON.

    Args:
        region_code: The eBird region code
        outdir: Output directory for the JSON file
        force: If True, download even if file already exists
    """
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)

    filepath = out_path / f"{region_code}.json"

    # Check if file already exists
    if filepath.exists() and not force:
        print(f"📁 File {filepath} already exists, skipping download")
        print(f"   Use --force to override existing files")
        return

    # Get credentials from environment variables
    username = os.getenv("EBIRD_USERNAME")
    password = os.getenv("EBIRD_PASSWORD")

    if not username or not password:
        raise ValueError(
            "Please set EBIRD_USERNAME and EBIRD_PASSWORD environment variables"
        )

    session = e2L.auth(username, password)

    # Call e2L.barchart directly
    data = e2L.load_barchart(session, region_code)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved {region_code} bar chart to {filepath}")


def create_manifest(barchart_dir="public/barchartData"):
    """
    Create a manifest.json file with region code to region name mapping
    for all JSON files in the barchartData folder.

    Args:
        barchart_dir: Directory containing the barchart JSON files
    """
    # Get API key from environment variables
    api_key = os.getenv("EBIRD_API_KEY")
    if not api_key:
        raise ValueError("Please set EBIRD_API_KEY environment variable")

    barchart_path = Path(barchart_dir)
    if not barchart_path.exists():
        print(f"❌ Directory {barchart_dir} does not exist")
        return

    # Load existing manifest if it exists
    manifest_path = barchart_path / "manifest.json"
    manifest = {}

    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            print(f"📖 Loaded existing manifest with {len(manifest)} regions")
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Could not read existing manifest: {e}")
            manifest = {}

    # Find all JSON files in the barchart directory (excluding manifest.json)
    json_files = [f for f in barchart_path.glob("*.json") if f.name != "manifest.json"]

    if not json_files:
        print(f"❌ No barchart JSON files found in {barchart_dir}")
        return

    # Identify which regions need to be fetched
    regions_to_fetch = []
    for json_file in json_files:
        region_code = json_file.stem
        if region_code not in manifest:
            regions_to_fetch.append(region_code)

    if not regions_to_fetch:
        print(f"✅ All {len(json_files)} regions already present in manifest")
        return

    print(
        f"Found {len(json_files)} JSON files. Need to fetch info for {len(regions_to_fetch)} new regions..."
    )

    for region_code in regions_to_fetch:
        print(f"Fetching info for region: {region_code}")

        # Fetch region information
        region_info = fetch_region_info(region_code, api_key)

        if region_info and "result" in region_info:
            manifest[region_code] = region_info
            print(f"  ✅ {region_code}: {region_info['result']}")
        else:
            # Fallback to using the region code as name if API call fails
            manifest[region_code] = region_code
            print(f"  ⚠️  {region_code}: Using region code as fallback name")

    # Save updated manifest to the same directory as the barchart data
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    if regions_to_fetch:
        print(f"✅ Updated manifest with {len(regions_to_fetch)} new regions")
    print(f"✅ Saved manifest to {manifest_path}")
    print(f"📋 Manifest now contains {len(manifest)} regions total")


def download_multiple_regions(
    region_codes: List[str],
    outdir: str = "public/barchartData",
    force: bool = False,
    delay: float = 1.0,
) -> None:
    """
    Download bar chart data for multiple regions with optional delay between requests.

    Args:
        region_codes: List of eBird region codes to download
        outdir: Output directory for JSON files
        force: If True, download even if file already exists
        delay: Delay in seconds between downloads (to be respectful to eBird servers)
    """
    print(f"📋 Starting batch download for {len(region_codes)} regions...")
    print(f"📁 Output directory: {outdir}")
    print(f"⏱️  Delay between requests: {delay}s")
    print("-" * 50)

    successful_downloads = []
    failed_downloads = []
    skipped_downloads = []

    for i, region_code in enumerate(region_codes, 1):
        print(f"\n[{i}/{len(region_codes)}] Processing region: {region_code}")

        try:
            # Check if file exists and should be skipped
            filepath = Path(outdir) / f"{region_code}.json"
            if filepath.exists() and not force:
                print(
                    f"⏭️  Skipping {region_code} (file exists, use --force to override)"
                )
                skipped_downloads.append(region_code)
                continue

            # Download the region data
            download_barchart(region_code, outdir=outdir, force=force)
            successful_downloads.append(region_code)

            # Add delay between requests (except for the last one)
            if i < len(region_codes) and delay > 0:
                print(f"⏳ Waiting {delay}s before next download...")
                time.sleep(delay)

        except Exception as e:
            print(f"❌ Failed to download {region_code}: {e}")
            failed_downloads.append(region_code)
            continue

    # Print summary
    print("\n" + "=" * 50)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 50)
    print(f"✅ Successful downloads: {len(successful_downloads)}")
    if successful_downloads:
        for region in successful_downloads:
            print(f"   - {region}")

    print(f"⏭️  Skipped (already exist): {len(skipped_downloads)}")
    if skipped_downloads:
        for region in skipped_downloads:
            print(f"   - {region}")

    print(f"❌ Failed downloads: {len(failed_downloads)}")
    if failed_downloads:
        for region in failed_downloads:
            print(f"   - {region}")

    if successful_downloads:
        print(f"\n🔄 Don't forget to update the manifest:")
        print(f"   python scripts/download_barchart.py --create-manifest")


def load_regions_from_file(filepath: str) -> List[str]:
    """
    Load region codes from a text file (one per line).

    Args:
        filepath: Path to file containing region codes

    Returns:
        List of region codes
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            regions = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
        print(f"📄 Loaded {len(regions)} regions from {filepath}")
        return regions
    except FileNotFoundError:
        print(f"❌ Error: File {filepath} not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file {filepath}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download eBird bar chart data and create manifest with batch support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download single region
  python scripts/download_barchart.py CH
  
  # Download multiple regions
  python scripts/download_barchart.py CH FR DE IT
  
  # Download from file
  python scripts/download_barchart.py --from-file regions.txt
  
  # Download with custom delay and force overwrite
  python scripts/download_barchart.py CH FR --delay 2 --force
  
  # Create manifest after downloads
  python scripts/download_barchart.py --create-manifest
        """,
    )

    # Mutually exclusive group for region specification
    region_group = parser.add_mutually_exclusive_group()
    region_group.add_argument(
        "regions", nargs="*", help="One or more region codes (e.g., CH FR DE)"
    )
    region_group.add_argument(
        "--from-file",
        metavar="FILE",
        help="Load region codes from a text file (one per line)",
    )

    # Other options
    parser.add_argument("--outdir", default="public/barchartData", help="Output folder")
    parser.add_argument(
        "--create-manifest",
        action="store_true",
        help="Create manifest.json for all existing barchart files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download even if file already exists",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between downloads (default: 1.0)",
    )

    args = parser.parse_args()

    if args.create_manifest:
        create_manifest(args.outdir)
    elif args.from_file:
        region_codes = load_regions_from_file(args.from_file)
        if len(region_codes) == 1:
            download_barchart(region_codes[0], outdir=args.outdir, force=args.force)
        else:
            download_multiple_regions(
                region_codes, outdir=args.outdir, force=args.force, delay=args.delay
            )
    elif args.regions:
        if len(args.regions) == 1:
            download_barchart(args.regions[0], outdir=args.outdir, force=args.force)
        else:
            download_multiple_regions(
                args.regions, outdir=args.outdir, force=args.force, delay=args.delay
            )
    else:
        parser.error(
            "Please specify region code(s), use --from-file, or use --create-manifest"
        )
