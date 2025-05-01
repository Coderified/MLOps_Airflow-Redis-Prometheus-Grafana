import traceback #for tracking error
import sys

class CustomException(Exception):

    #create constructor

    def __init__(self,error_message,error_detail:sys):
        super().__init__(error_message)
        self.error_message = self.get_detailed_error_message(error_message,error_detail)

    @staticmethod
    def get_detailed_error_message(error_message,error_detail:sys):
        _,_,exc_traceback = traceback.sys.exc_info()
        file_name = exc_traceback.tb_frame.f_code.co_filename #shows name of file the error occured
        line_num = exc_traceback.tb_lineno

        return f"Error Occured in {file_name}, {line_num} : {error_message}"
    
    def __str__(self):
        return self.error_message

        #gives text rep of error message
