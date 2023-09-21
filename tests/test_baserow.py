import pytest
from baserowapi.baserow import Baserow
from pytest_mock import mocker
import logging
import requests

def test_get_table_constructor_called_with_correct_arguments(mocker):
    # Create an instance of Baserow
    baserow_instance = Baserow()

    # Mock the Table class as it is imported in the Baserow class
    MockedTable = mocker.patch('baserowapi.baserow.Table')
    print(MockedTable.call_args_list)

    # Call the get_table method
    table_id = 123
    table = baserow_instance.get_table(table_id)

    # Assertions
    MockedTable.assert_called_once_with(123, baserow_instance)
    assert table is MockedTable.return_value

def test_configure_logging_streamhandler_added(mocker):
    baserow = Baserow()
    
    mock_basicConfig = mocker.patch('logging.basicConfig')
    baserow.configure_logging('DEBUG', None)
    
    # Check if StreamHandler was in the handlers list
    _, kwargs = mock_basicConfig.call_args
    assert any(isinstance(handler, logging.StreamHandler) for handler in kwargs['handlers'])

def test_configure_logging_filehandler_added_when_log_file_provided(mocker):
    baserow = Baserow()
    
    mock_basicConfig = mocker.patch('logging.basicConfig')
    baserow.configure_logging('DEBUG', 'test.log')
    
    # Check if FileHandler was in the handlers list
    _, kwargs = mock_basicConfig.call_args
    print(mock_basicConfig.call_args)
    handlers_arg = mock_basicConfig.call_args.kwargs.get('handlers', [])
    print(handlers_arg)

    assert any('test.log' in str(handler) for handler in handlers_arg)

def test_configure_logging_correct_level(mocker):
    baserow = Baserow()
    
    mock_basicConfig = mocker.patch('logging.basicConfig')
    baserow.configure_logging('DEBUG', None)
    
    # Check if the correct logging level was passed
    _, kwargs = mock_basicConfig.call_args
    assert kwargs['level'] == 'DEBUG'

# ========== make_api_request tests ==================

def test_make_api_request_get_request(mocker):
    baserow = Baserow()
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = '{"message": "Hello World"}'
    mock_response.json.return_value = {"message": "Hello World"}
    
    mocker.patch.object(baserow.session, 'request', return_value=mock_response)
    
    response = baserow.make_api_request("/test_endpoint")
    
    assert response == {"message": "Hello World"}

def test_make_api_request_post_request_with_data(mocker):
    baserow = Baserow()
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = '{"message": "Data received"}'
    mock_response.json.return_value = {"message": "Data received"}
    
    mocker.patch.object(baserow.session, 'request', return_value=mock_response)
    
    response = baserow.make_api_request("/test_endpoint", method="POST", data={"key": "value"})
    
    assert response == {"message": "Data received"}

def test_make_api_request_delete_request(mocker):
    baserow = Baserow()
    
    mock_response = mocker.Mock()
    mock_response.status_code = 204
    
    mocker.patch.object(baserow.session, 'request', return_value=mock_response)
    
    response = baserow.make_api_request("/test_endpoint", method="DELETE")
    
    assert response == 204

def test_make_api_request_request_timeout(mocker):
    baserow = Baserow()
    
    mocker.patch.object(baserow.session, 'request', side_effect=requests.exceptions.Timeout)
    
    with pytest.raises(requests.exceptions.Timeout):
        baserow.make_api_request("/test_endpoint")

def test_make_api_request_bad_request(mocker):
    baserow = Baserow()

    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.text = 'Bad request'
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("An error occurred")
    mock_response.raise_for_status.response = mock_response

    mocker.patch.object(baserow.session, 'request', return_value=mock_response)

    with pytest.raises(Exception, match="Bad request to"):
        baserow.make_api_request("/test_endpoint")

@pytest.mark.parametrize(
    "status_code,expected_error",
    [
        (401, "Unauthorized request to {url}. Accessing an endpoint without a valid database token."),
        (404, "Resource not found at {url}. Row or table is not found."),
        (413, "Request entity too large at {url}. The request exceeded the maximum allowed payload size."),
        (500, "Internal server error at {url}. The server encountered an unexpected condition."),
        (502, "Bad gateway at {url}. Baserow is restarting or an unexpected outage is in progress."),
        (503, "Service unavailable at {url}. The server could not process your request in time.")
    ]
)
def test_make_api_request_error_codes(mocker, status_code, expected_error):
    # Setup the Baserow client
    baserow = Baserow()
    endpoint_url = "https://api.baserow.io/test_endpoint"

    # Create a mock response with the specific status code
    mock_response = mocker.Mock()
    mock_response.status_code = status_code
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException()

    # Mock the session request to return our mock response
    mocker.patch.object(baserow.session, 'request', return_value=mock_response)

    # Use pytest.raises to expect the exception
    with pytest.raises(Exception, match=expected_error.format(url=endpoint_url)):
        baserow.make_api_request("/test_endpoint")

def test_parse_response_no_body(mocker):
    baserow = Baserow()
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = ""

    result = baserow.parse_response(mock_response, "GET", "https://api.baserow.io/test_endpoint")
    assert result is None

def test_parse_response_204_status_code(mocker):
    baserow = Baserow()
    mock_response = mocker.Mock()
    mock_response.status_code = 204
    mock_response.text = ""

    result = baserow.parse_response(mock_response, "GET", "https://api.baserow.io/test_endpoint")
    assert result == 204

def test_parse_response_valid_json(mocker):
    baserow = Baserow()
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = '{"data": "valid_json"}'
    mock_response.json.return_value = {"data": "valid_json"}

    result = baserow.parse_response(mock_response, "GET", "https://api.baserow.io/test_endpoint")
    assert result == {"data": "valid_json"}

def test_parse_response_invalid_json(mocker):
    baserow = Baserow()
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>This is not JSON</html>"
    mock_response.json.side_effect = ValueError("No JSON object could be decoded")

    result = baserow.parse_response(mock_response, "GET", "https://api.baserow.io/test_endpoint")
    assert result == "<html>This is not JSON</html>"

def test_perform_request_unexpected_error(mocker):
    baserow = Baserow()
    
    mock_error = requests.exceptions.RequestException("Unexpected error")
    mocker.patch.object(baserow.session, 'request', side_effect=mock_error)

    with pytest.raises(Exception, match="Unexpected error occurred while making a request to"):
        baserow.perform_request("GET", "https://api.baserow.io/test_endpoint", {}, None, 10)

def test_perform_request_connection_error(mocker):
    baserow = Baserow()
    
    mock_error = requests.exceptions.ConnectionError("Failed to establish a connection")
    mocker.patch.object(baserow.session, 'request', side_effect=mock_error)

    with pytest.raises(Exception, match="Unexpected error occurred while making a request to"):
        baserow.perform_request("GET", "https://api.baserow.io/test_endpoint", {}, None, 10)

def test_perform_request_dns_resolution_failure(mocker):
    baserow = Baserow()

    mock_error = requests.exceptions.RequestException("DNS resolution failed")
    mocker.patch.object(baserow.session, 'request', side_effect=mock_error)

    with pytest.raises(Exception, match="Unexpected error occurred while making a request to"):
        baserow.perform_request("GET", "https://api.baserow.io/test_endpoint", {}, None, 10)

def test_get_combined_headers_no_additional_headers():
    baserow = Baserow()

    headers = baserow.get_combined_headers(None)
    
    # Assuming self.headers has a default value in the class initialization
    expected_headers = baserow.headers
    
    assert headers == expected_headers

def test_get_combined_headers_with_additional_headers():
    baserow = Baserow()

    additional_headers = {"X-Custom-Header": "test_value"}
    headers = baserow.get_combined_headers(additional_headers)
    
    expected_headers = {**baserow.headers, **additional_headers}
    
    assert headers == expected_headers

def test_get_combined_headers_overlapping_headers():
    baserow = Baserow()

    # Let's assume "Authorization" is a key in the default headers
    overlapping_header = {"Authorization": "Bearer new_token"}
    headers = baserow.get_combined_headers(overlapping_header)
    
    # The new header should take precedence
    expected_headers = {**baserow.headers, **overlapping_header}
    
    assert headers == expected_headers

def test_make_api_request_with_headers(mocker):
    baserow = Baserow()

    additional_headers = {"X-Custom-Header": "test_value"}
    
    # Mock the HTTP request
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mocker.patch.object(baserow.session, 'request', return_value=mock_response)
    
    baserow.make_api_request("/test_endpoint", "GET", headers=additional_headers)
    
    # Check if the headers used in the request include our additional header
    used_headers = baserow.session.request.call_args[1]['headers']
    
    assert "X-Custom-Header" in used_headers
    assert used_headers["X-Custom-Header"] == "test_value"

