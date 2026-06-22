# Friends Photos

Simple web app to upload photos to an AWS S3 bucket and download all stored photos as a ZIP archive.

## Project structure

```
friends-photos/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── s3.py
│   ├── zip_utils.py
│   ├── routes.py
│   └── schemas.py
├── static/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── .env
├── requirements.txt
└── README.md
```

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure AWS credentials in `.env`:

   ```env
   AWS_ACCESS_KEY_ID=your_access_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_access_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket-name
   ENDPOINT_URL=https://your-s3-endpoint
   APP_PASSWORD=choose-a-strong-shared-password
   ```

4. Ensure the S3 bucket exists and your IAM user has permissions for `s3:PutObject`, `s3:GetObject`, and `s3:ListBucket`.

## Run

From the project root:

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## API

| Method | Endpoint       | Description                          |
|--------|----------------|--------------------------------------|
| GET    | `/api/auth/check` | Verify password (HTTP Basic Auth) |
| POST   | `/api/upload`  | Upload images to S3 (requires auth)  |
| GET    | `/api/download`| Download all bucket objects as a ZIP (requires auth) |

Upload and download require HTTP Basic Auth. Use any username and the password from `APP_PASSWORD`.

Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
