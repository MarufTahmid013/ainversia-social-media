#!/usr/bin/env python3
"""Import one GitHub issue-attached image into the public AinVersia media directory."""
import os,re,sys,urllib.request,urllib.parse,pathlib,subprocess
body=pathlib.Path(os.environ["ISSUE_BODY_FILE"]).read_text(encoding="utf-8")
issue=os.environ["ISSUE_NUMBER"]
# GitHub issue attachments use GitHub-owned attachment hosts.
links=re.findall(r'https://[^\s)<>]+',body)
allowed={"github.com","user-images.githubusercontent.com","github-production-user-asset-6210df.s3.amazonaws.com"}
candidates=[]
for raw in links:
    url=raw.rstrip('.,]')
    p=urllib.parse.urlparse(url)
    if p.scheme!="https": continue
    if p.hostname=="github.com" and p.path.startswith("/user-attachments/assets/"): candidates.append(url)
    elif p.hostname=="user-images.githubusercontent.com": candidates.append(url)
if len(candidates)!=1: sys.exit("Expected exactly one GitHub-hosted image attachment in issue body")
url=candidates[0]
req=urllib.request.Request(url,headers={"User-Agent":"AinVersia-Media-Importer"})
with urllib.request.urlopen(req,timeout=30) as resp:
    data=resp.read(8*1024*1024+1)
    content_type=resp.headers.get("Content-Type","").split(";")[0]
if len(data)>8*1024*1024: sys.exit("Image exceeds 8MB")
if data.startswith(b"\x89PNG\r\n\x1a\n"): ext="png"
elif data.startswith(b"\xff\xd8\xff"): ext="jpg"
else: sys.exit("Unsupported image: expected PNG or JPEG")
# Filename specified in issue body: 'filename: YYYY-MM-DD-slug'
m=re.search(r'(?im)^filename:\s*([a-z0-9][a-z0-9-]{2,70})\s*$',body)
if not m: sys.exit("Include filename: YYYY-MM-DD-short-slug in issue body")
name=m.group(1)
dest=pathlib.Path("media/posts")/(name+"."+ext)
dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists(): sys.exit("Refusing to overwrite existing approved image")
dest.write_bytes(data)
subprocess.run(["git","add","--",str(dest)],check=True)
subprocess.run(["git","commit","-m",f"Import approved image from issue #{issue}: {name}"],check=True)
subprocess.run(["git","push"],check=True)
print(f"IMAGE_URL=https://raw.githubusercontent.com/MarufTahmid013/ainversia-social-media/main/{dest}")
