#!/usr/bin/env bash

set -eou pipefail

output_dir="${1:-/release}"

buildstamp="$(date -u +%Y%m%d-%H%M%S)"
githash=`git rev-parse HEAD`

mkdir -p $output_dir

just compile
mv stacklet-admin $output_dir/

cat > $output_dir/installer.cfg <<EOF
built=$buildstamp
githash=$githash
EOF

tar -C $output_dir -czf platform-cli-$githash.tar.gz .

aws s3 cp platform-cli-$githash.tar.gz s3://stacklet-compiled-assets/platform-cli/builds/$githash/ --sse AES256 --acl bucket-owner-full-control --metadata githash="${githash}"
