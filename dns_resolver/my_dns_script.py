import json
import dns.resolver


class Dns_resolver:

    def __init__(self):
        pass

    def get_records(self, domain):

        record_types = [
            'A',
            'AAAA',
            'ALIAS',
            'NS',
            'CNAME',
            'SOA',
            'MX',
            'TXT',
            'SRV',
            'PTR',       
        ]

        records = []

        for record_type in record_types:

            try:
                data = dns.resolver.query(domain, record_type)

                for rdata in data:
                    records.append(record_type + ' ' + rdata.to_text())      
                    
            except Exception:
                pass

        return records
        
    def dns_domain(self):
        
        domains = ['google.com', 'baidu.com', 'amazon.com']  # Insert domains required 
        dict_record = {}

        for domain in domains:
            records = self.get_records(domain)
            commands = {}
           
            for record in records:
                command, description = record.strip().split(None, 1)
                commands[command] = description.split()
            dict_record[domain] = commands
            
        with open("domain.json", 'w') as json_file:
            json.dump(dict_record, json_file, indent=2)

        return dict_record

if __name__ == "__main__":
    Dns_resolver().dns_domain()
