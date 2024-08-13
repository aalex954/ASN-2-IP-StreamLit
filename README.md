# ASN-2-IP-StreamLit
ASN-2-IP rewritten in Python with a StreamLit UI.

Retrieves all the Autonomous System (AS) Numbers associated with an organization and then gets a deduplicated list of IPv4 and IPv6 subnets controlled by each AS number.

## Setup

```bash
pip install streamlit requests pandas
```
```bash
streamlit run app.py
```
## Usage

- Input the organization name in the sidebar and click "Find ASN IP Ranges".
- Follow the progress indicated by the bar and text updates.
- Download a new line deliniated list of IPv4 and IPv6 subnets.

## Screenshot

![image](https://github.com/user-attachments/assets/8861dc6a-5a64-40ba-8481-b5c9774853ee)

