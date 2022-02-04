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

tar -C $output_dir -czf stacklet-admin-$githash.tar.gz .

aws s3 cp stacklet-admin-$githash.tar.gz s3://stacklet-compiled-assets/stacklet-admin/builds/$githash/ --sse AES256 --acl bucket-owner-full-control --metadata githash="${githash}"
