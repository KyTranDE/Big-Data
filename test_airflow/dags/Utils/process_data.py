import email
import uuid
import pandas as pd

def splitEmailAddresses(emailString: str):
    '''
    The function splits a comma-separated string of email addresses into a unique list.
    
    Args:
        emailString: A string containing email addresses separated by commas.
        
    Returns:
        A list of unique email addresses.
    '''
    if emailString:
        addresses = emailString.split(',')
        uniqueAddresses = list(frozenset(map(lambda x: x.strip(), addresses)))
        return uniqueAddresses
    return []

def extractEmailDetailsFromRawText(rawEmail: str):
    '''
    The function extracts relevant details from a raw email message string.
    
    Args:
        rawEmail: A string representing the raw email message.
        
    Returns:
        A Row object containing the extracted email details.
    '''
    emailMessage = email.message_from_string(rawEmail)
    emailContentParts = []
    for part in emailMessage.walk():
        if part.get_content_type() == 'text/plain':
            emailContentParts.append(part.get_payload())

    emailContent = ''.join(emailContentParts)

    fromAddresses = splitEmailAddresses(emailMessage.get("From"))
    toAddresses = splitEmailAddresses(emailMessage.get("To"))
    ccEmail = splitEmailAddresses(emailMessage.get("Cc"))
    return emailMessage.get("Date"), fromAddresses, toAddresses, emailMessage.get("Subject"), ccEmail, emailContent

def process_emails(sample_df):
    """
    Xử lý dữ liệu email từ DataFrame chứa các email đã chọn lọc.
    
    Args:
        sample_df: DataFrame chứa các email đã chọn lọc.
        
    Returns:
        emails_data: Danh sách các email đã xử lý.
        addresses_data: Danh sách các địa chỉ email đã xử lý.
        email_addresses_data: Danh sách các cặp email và địa chỉ email đã xử lý.
    """
    emails_data = []
    addresses_data = []
    email_addresses_data = []
    addresses_dict = {}

    for index, row in sample_df.iterrows():
        rawEmail = row['message']
        date, fromAddresses, toAddresses, subject, ccEmail, emailContent = extractEmailDetailsFromRawText(rawEmail)

        email_id = str(uuid.uuid4())

        emails_data.append({
            'email_id': email_id,
            'date': date,
            'subject': subject,
            'content': emailContent
        })

        allAddresses = {
            'from': fromAddresses,
            'to': toAddresses,
            'cc': ccEmail
        }

        for role, addresses in allAddresses.items():
            for address in addresses:
                if address not in addresses_dict:
                    address_id = str(uuid.uuid4())
                    addresses_data.append({
                        'address_id': address_id,
                        'email_address': address
                    })
                    addresses_dict[address] = address_id

                email_addresses_data.append({
                    'email_id': email_id,
                    'address_id': addresses_dict[address],
                    'role': role
                })

    return emails_data, addresses_data, email_addresses_data
