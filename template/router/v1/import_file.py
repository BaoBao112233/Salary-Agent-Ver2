"""
Import File Router
Endpoint để xử lý 3 file đầu vào (chấm công, thông tin lương, template) và tạo file lương kết quả
"""
import os
import uuid
import logging
import math
from fastapi import APIRouter, BackgroundTasks, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from template.agent.agent import Agent
from template.schemas.model import ChatRequestAPI
from template.services.aws_service import S3Service
from template.services.read_excel_xlsx import read_excel_to_array, matching_data
from template.services.portgre_services import insert_employee_data, create_table


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Import File"])

# Initialize agent and S3 service
import_agent = Agent()
s3_service = S3Service()


def sanitize_for_json(obj):
    """Recursively sanitize data to be JSON-compliant by replacing NaN, Infinity with None"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj


@router.post("/import_file")
async def import_file(
    session_id: int = Form(..., description="ID phiên làm việc"),
    user_id: int = Form(..., description="ID người dùng"),
    background_tasks: BackgroundTasks = None,
    attendance_file: UploadFile = File(..., description="File chấm công của nhân viên (.xlsx)"),
    salary_info_file: UploadFile = File(..., description="File thông tin lương cơ bản (.xlsx)"),
    template_file: UploadFile = File(..., description="File template tính lương (.xlsx)"),
    
):
    """
    Import và xử lý 3 file để tạo file lương kết quả
    
    ## Mô tả
    Endpoint này nhận 3 file đầu vào:
    - **session_id**: ID phiên làm việc
    - **user_id**: ID người dùng
    - **attendance_file**: File chứa thông tin chấm công của các nhân viên
    - **salary_info_file**: File chứa thông tin lương cơ bản (mỗi nhân viên có mức lương khác nhau)
    - **template_file**: File template dùng để tính lương (có công thức tính toán)
    
    ## Agent sẽ:
    - Phân tích từng file để hiểu cấu trúc và dữ liệu
    - Phân tích đầy đủ các sheet trong mỗi file
    - Kiểm tra xem thiếu thông tin gì để tính được kết quả
    - Sử dụng AI để đánh giá tính đầy đủ của dữ liệu
    - Gộp dữ liệu và tính toán lương
    - Tạo file Excel kết quả
    
    ## Output
    - File Excel chứa kết quả tính lương
    - Thông tin phân tích chi tiết về từng file
    - Cảnh báo về dữ liệu thiếu (nếu có)
    
    ## Ví dụ sử dụng
    ```bash
    curl -X POST "http://localhost:8000/api/v1/import_file" \\
      -F "session_id=your_session_id" \\
      -F "user_id=your_user_id" \\
      -F "attendance_file=@cham_cong.xlsx" \\
      -F "salary_info_file=@thong_tin_luong.xlsx" \\
      -F "template_file=@template_tinh_luong.xlsx"
    ```
    """
    
    unique_id = str(uuid.uuid4())
    
    # Initialize path variables
    attendance_path = None
    salary_info_path = None
    template_path = None
    
    try:
        # Validate file extensions
        for file in [attendance_file, salary_info_file, template_file]:
            if not file.filename.endswith(('.xlsx', '.xls')):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} must be Excel format (.xlsx or .xls)"
                )
        
        # Save uploaded files
        logger.info(f"Processing files for request {unique_id}")
        create_table()

        attendance_path = f"uploads/attendance_{unique_id}.xlsx"
        salary_info_path = f"uploads/salary_info_{unique_id}.xlsx"
        template_path = f"uploads/template_{unique_id}.xlsx"
        output_path = f"outputs/result_{unique_id}.xlsx"
        
        logger.info("Saving uploaded files...")
        with open(attendance_path, "wb") as f:
            f.write(await attendance_file.read())
        logger.info(f"✓ Saved attendance file: {attendance_file.filename}")
        
        with open(salary_info_path, "wb") as f:
            f.write(await salary_info_file.read())
        logger.info(f"✓ Saved salary info file: {salary_info_file.filename}")
        
        with open(template_path, "wb") as f:
            f.write(await template_file.read())
        logger.info(f"✓ Saved template file: {template_file.filename}")
        
        # Upload input files to S3
        try:
            s3_attendance_key = s3_service.upload_file(
                attendance_path, "inputs", f"attendance_{unique_id}.xlsx"
            )
            s3_salary_key = s3_service.upload_file(
                salary_info_path, "inputs", f"salary_info_{unique_id}.xlsx"
            )
            s3_template_key = s3_service.upload_file(
                template_path, "inputs", f"template_{unique_id}.xlsx"
            )
            logger.info(f"✓ Uploaded input files to S3")
        except Exception as e:
            logger.warning(f"Could not upload to S3: {str(e)}")

        # Read attendance data and insert into database
        logger.info("Reading Excel files...")
        attendance_data = read_excel_to_array(attendance_path)
        salary_data = read_excel_to_array(salary_info_path)

        logger.info("Matching attendance and salary data...")
        combined_data = matching_data(attendance_data, salary_data)
        
        logger.info(f"Inserting {len(combined_data)} employees into database...")
        inserted_count = insert_employee_data(combined_data)
        logger.info(f"✓ Successfully inserted {inserted_count} employees")
        
        return {
            "success": True,
            "data": inserted_count
        }
        
        # # Process files using agent
        # logger.info("Starting agent analysis and processing...")
        # result = import_agent.analyze_and_process(
        #     attendance_file=attendance_path,
        #     salary_info_file=salary_info_path,
        #     template_file=template_path,
        #     output_file=output_path
        # )
        
        # # Check if output file was created
        # if not os.path.exists(output_path):
        #     raise HTTPException(
        #         status_code=500,
        #         detail="Failed to generate output file"
        #     )
        
        # # Upload output file to S3
        # try:
        #     s3_output_key = s3_service.upload_file(
        #         output_path, "outputs", f"result_{unique_id}.xlsx"
        #     )
        #     logger.info(f"✓ Uploaded output file to S3: {s3_output_key}")
        #     s3_download_url = s3_service.generate_presigned_url(s3_output_key)
        # except Exception as e:
        #     logger.warning(f"Could not upload output to S3: {str(e)}")
        #     s3_download_url = None
        
        # # Clean up uploaded input files
        # try:
        #     for path in [attendance_path, salary_info_path, template_path]:
        #         if os.path.exists(path):
        #             os.remove(path)
        #     logger.info("✓ Cleaned up uploaded files")
        # except Exception as e:
        #     logger.warning(f"Could not clean up files: {str(e)}")
        
        # # Prepare response
        # response_data = {
        #     "success": True,
        #     "message": "Files processed successfully",
        #     "unique_id": unique_id,
        #     "output_file": os.path.basename(output_path),
        #     "download_link": f"/download/{os.path.basename(output_path)}",
        #     "s3_download_url": s3_download_url,
        #     "analysis": {
        #         "template_info": result.get("template_info", {}),
        #         "employee_summary": result.get("employee_summary", {}),
        #         "processing_result": result.get("processing_result", {})
        #     },
        #     "employee_details": result.get("employee_details", [])
        # }
        
        # # Add validation results if available
        # validation_result = result.get("validation_result")
        # if validation_result:
        #     response_data["validation"] = {
        #         "success": validation_result.get("success", False),
        #         "total_errors": validation_result.get("summary", {}).get("total_errors", 0),
        #         "total_warnings": validation_result.get("summary", {}).get("total_warnings", 0),
        #         "errors": validation_result.get("errors", []),
        #         "warnings": validation_result.get("warnings", [])[:10]  # Limit to 10 warnings in API response
        #     }
            
        #     # Add validation errors to warnings
        #     if validation_result.get("errors"):
        #         if "warnings" not in response_data:
        #             response_data["warnings"] = []
        #         response_data["warnings"].extend([
        #             f"⚠️ Validation error: {err['message']}" 
        #             for err in validation_result["errors"][:3]
        #         ])
        
        # # Separate complete and incomplete employees
        # complete_employees = [emp for emp in result.get("employee_details", []) if emp["is_complete"]]
        # incomplete_employees = [emp for emp in result.get("employee_details", []) if not emp["is_complete"]]
        
        # # Add summary messages
        # if incomplete_employees:
        #     response_data["warnings"] = [
        #         f"⚠️ {len(incomplete_employees)} nhân viên thiếu thông tin và không được tính lương"
        #     ]
        #     response_data["incomplete_employees"] = [
        #         {
        #             "employee_id": emp["employee_id"],
        #             "employee_name": emp["employee_name"],
        #             "missing_fields": emp["missing_fields"]
        #         }
        #         for emp in incomplete_employees
        #     ]
        
        # if complete_employees:
        #     response_data["success_message"] = f"✅ Đã tính lương cho {len(complete_employees)} nhân viên"
        
        # # Sanitize response data to remove NaN/Infinity values before JSON serialization
        # response_data = sanitize_for_json(response_data)
        
        # logger.info(f"✓ Request {unique_id} completed successfully")
        # return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}", exc_info=True)
        
        # Clean up files on error
        for path in [attendance_path, salary_info_path, template_path]:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing files: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_result(filename: str):
    """Download file kết quả"""
    file_path = f"outputs/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
