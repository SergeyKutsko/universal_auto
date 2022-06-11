from app.models import PaymentsOrder
import csv
import datetime

def run():
    with open('seeds/20220501-20220531-payments_order.csv') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header

        for row in reader:
            print(row)
            film = PaymentsOrder(transaction_uuid = row[0],
                                 driver_uuid = row[1],
                                 drievr_name = row[2],
                                 drievr_second_name = row[3],
                                 trip_uuid = row[4],
                                 trip_description = row[5],
                                 organization_name = row[6],
                                 organization_nickname = row[7],
                                 transaction_time = datetime.datetime.strptime(row[8], "%Y-%m-%d %H:%M:%S.%f %z EEST"),
                                 paid_to_you = row[9],
                                 your_earnings = row[10],
                                 cash = row[11],
                                 fare = row[12],
                                 tax = row[13],
                                 fare2 = row[14],
                                 service_tax = row[15],
                                 wait_time = row[16],
                                 out_of_city = row[17],
                                 tips = row[18],
                                 transfered_to_bank = row[19],
                                 ajustment_payment =row[20],
                                 cancel_payment = row[21])
            film.save()