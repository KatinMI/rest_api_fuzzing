from boofuzz import *
import logging

def log_server_response(target, fuzz_data_logger, session, *args, **kwargs):
    try:
        response = target.recv(4096)
        if response:
            fuzz_data_logger.log_check(f"Server response: {response}")
            logging.info(f"Server response: {response}")
    except Exception as e:
        fuzz_data_logger.log_check(f"Error reading response: {e}")

def main():
    connection = TCPSocketConnection("127.0.0.1", 8080)

    target = Target(
        connection=connection,
        callbacks=[log_server_response] 
    )
# Закомментил, так как они создают файлы с логами по 50 Гб каждый
    #txt_logger = FuzzLoggerText(file_handle=open("fuzz_log.txt", "w"))
    #csv_logger = FuzzLoggerCsv(file_handle=open("fuzz_log.csv", "w"))

    session = Session(
        post_test_case_callbacks=[log_server_response], 
        #fuzz_loggers=[txt_logger, csv_logger], 
        web_port=26000 
    )

    session.add_target(target)
    s_initialize("http_request")
    with s_block("request_line"):
        s_group("method", ["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH", "OPTIONS"])
        s_delim(" ")
        s_string("/")
        s_delim(" ")
        s_string("HTTP/1.1")
        s_static("\r\n")

    # zagolovki
    with s_block("headers"):
        # Host header
        s_static("Host: ")
        s_string("localhost")
        s_static("\r\n")
      
        # User-Agent
        s_static("User-Agent: ")
        s_group("user_agent", [
            "Boofuzz",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "curl/7.68.0"
        ])
        s_static("\r\n")

        # Content-Type
        s_static("Content-Type: ")
        s_group("content_type", [
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "application/json",
            "text/xml",
            "application/javascript"
        ])
        s_static("\r\n")

        s_static("Authorization: ")
        s_group("auth_type", ["Basic ", "Bearer "])
        with s_block("auth_value"):
            s_string("test")
            s_string("admin:password")
            s_string("!@#$%^&*()")
            s_string("A" * 1000)  # Длинное значение
        s_static("\r\n")

        s_static("Accept: ")
        s_string("*/*")
        s_string(", ")
        s_string("text/html,application/xhtml+xml")
        s_static("\r\n")

        s_static("Connection: ")
        s_group("connection", ["keep-alive", "close", "upgrade"])
        s_static("\r\n")

        s_static("X-Special-Chars: ")
        s_string("!\"#$%&'()*+,-./:;<=>?@[$$^_`{|}~")
        s_static("\r\n")

    s_static("Content-Length: ")
    s_size("body", output_format="ascii", inclusive=False)
    s_static("\r\n\r\n")

    with s_block("multipart_form_data"):
        s_static("--BOUNDARY\r\n")
        s_static("Content-Disposition: form-data; name=\"file\"; filename=\"test.txt\"\r\n")
        s_static("Content-Type: text/plain\r\n\r\n")
        s_string("This is a test file content")
        s_static("\r\n--BOUNDARY--\r\n")

    with s_block("long_values"):
        s_static("\r\n--LONG-VALUES--\r\n")
        s_string("A" * 10000)  # 10,000 A's
        s_string("\r\n")
        s_string("B" * 100000)  # 100,000 B's
        s_static("\r\n")

    with s_block("special_chars"):
        s_static("\r\n--SPECIAL-CHARS--\r\n")
        s_string("!\"#$%&'()*+,-./:;<=>?@[$$^_`{|}~")
        s_string("àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ")
        s_string("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
        s_string("%00%00%00%00")  # Null bytes
        s_string("\x00\x01\x02\x03\x04\x05")  # Binary data
        s_static("\r\n")

    with s_block("body"):
        s_string("test")
        s_string("key=value&key2=value2")
        s_string("{\"json\": \"test\"}")
        s_string("<xml><test>data</test></xml>")

    session.connect(s_get("http_request"))
    
    try:
        session.fuzz()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
    
