import boto3
import json
import os
import mimetypes
from botocore.exceptions import ClientError

def static_website_hosting(bucketname, region="us-east-1", site_folder="site_folder"):
    s3 = boto3.client("s3", region_name=region)

    # Step 1: Create a bucket
    try:
        s3.create_bucket(Bucket=bucketname)
        print(f"Bucket '{bucketname}' created.")
    except ClientError as e:
        print(f"Error creating bucket '{bucketname}': {e}")
        raise

    # Step 2: Delete "block public access" of the bucket
    try:
        s3.delete_public_access_block(Bucket=bucketname)
        print("Public access block removed.")
    except ClientError as e:
        print(f"Error removing public access block for '{bucketname}': {e}")
        raise

    # Step 3: Add Bucket Policy allowing public read access
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucketname}/*"]
        }]
    }

    try:
        s3.put_bucket_policy(
            Bucket=bucketname,
            Policy=json.dumps(policy)
        )
        print("Bucket policy applied successfully.")
    except ClientError as e:
        print(f"Error applying bucket policy to '{bucketname}': {e}")
        raise

    # Step 4: Enable static website hosting
    try:
        s3.put_bucket_website(
            Bucket=bucketname,
            WebsiteConfiguration={
                'ErrorDocument': {'Key': 'error.html'},
                'IndexDocument': {'Suffix': 'index.html'}
            }
        )
        print(f"Static website enabled for bucket '{bucketname}'.")
    except ClientError as e:
        print(f"Error enabling static website for '{bucketname}': {e}")
        raise

    # Step 5: Upload files from local site folder
    if not os.path.exists(site_folder):
        print(f"The folder '{site_folder}' does not exist.")
        return

    for filename in os.listdir(site_folder):
        filepath = os.path.join(site_folder, filename)
        file_mime_type, _ = mimetypes.guess_type(filename)
        file_mime_type = file_mime_type or "binary/octet-stream"

        try:
            s3.upload_file(
                filepath,
                bucketname,
                filename,
                ExtraArgs={'ContentType': file_mime_type}
            )
            print(f"File '{filename}' uploaded to bucket '{bucketname}'.")
        except ClientError as e:
            print(f"Error uploading file '{filename}' to bucket '{bucketname}': {e}")
            raise

    # Step 6: Print the website URL
    print(f"\nWebsite is live at: http://{bucketname}.s3-website-{region}.amazonaws.com")

# ---------------- Execution ----------------
if __name__ == "__main__":
    bucketname = "gandhi-static-website-190102077"  # Must be globally unique
    static_website_hosting(bucketname, site_folder="site_folder")
