from django.shortcuts import render

import boto3
import os
from botocore.exceptions import NoCredentialsError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import urllib.parse 

class S3FileFetchAPIView(APIView):
    def get(self, request, *args, **kwargs):
        class_name = kwargs.get('class_name')  # Extract class_name from kwargs
        subject = kwargs.get('subject') 
        bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
        region_name = os.getenv("AWS_REGION_NAME")
        
        print("filesfetch")
        # Initialize the S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region_name,
        )

        try:
            s3_folder_path = f"{class_name}/books/{subject}/"

            # List objects in the specified folder
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder_path)
            # Check if there are files in the folder
            if 'Contents' not in response:
                return Response(
                    {"message": "No files found in 'class1' folder"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Prepare PDF file details
            pdf_files = []
            for obj in response["Contents"]:
                file_name = obj["Key"].split("/")[-1]
                if file_name.lower().endswith('.pdf'):  # Filter for PDF files
                    # URL-encode the file name
                    encoded_key = urllib.parse.quote(obj["Key"])
                    file_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{encoded_key}"
                    pdf_files.append({
                        "file_name": file_name,
                        "subject":file_name.split(" ")[3],
                        "class":file_name.split(" ")[2],
                        "last_modified": obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
                        "url": file_url,
                    })

            if not pdf_files:
                return Response(
                    {"message": "No PDF files found in folder"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response({"pdf_files": pdf_files}, status=status.HTTP_200_OK)

        except NoCredentialsError:
            return Response(
                {"error": "AWS credentials not found"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class S3ImageFetchAPIView(APIView):
    def get(self, request, *args, **kwargs):
        class_name = kwargs.get('class_name')
        bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
        region_name = os.getenv("AWS_REGION_NAME")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region_name,
        )    


        if not class_name:
            return Response({"error": "Class name is required"}, status=status.HTTP_400_BAD_REQUEST)

        s3_folder_path = f"{class_name}/"

        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder_path)
            if 'Contents' not in response:
                
                return Response({"message": "No images found"}, status=status.HTTP_404_NOT_FOUND)

            image_files = []
            for obj in response["Contents"]:
                file_name = obj["Key"].split("/")[-1]
                
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):  
                    encoded_key = urllib.parse.quote(obj["Key"])
                    file_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{encoded_key}"
                    image_files.append({
                        "file_name": file_name,
                        "url": file_url,
                    })

            if not image_files:
                return Response({"message": "No image files found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"images": image_files}, status=status.HTTP_200_OK)

        except NoCredentialsError:
            return Response({"error": "AWS credentials not found"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
