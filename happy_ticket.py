import concurrent.futures
import itertools

def happy_ticket(ticket):
    first_half = ticket[:3]
    second_half = ticket[3:]
    return sum(map(int, first_half)) == sum(map(int, second_half))

def generate_tickets(ticket_length):
    for ticket in itertools.product('0123456789', repeat=ticket_length):
        yield ''.join(ticket)


def count_tickets(ticket_length, num_threads=4):
    happy_ticket_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(happy_ticket, ticket) for ticket in generate_tickets(ticket_length)]

        for future in concurrent.futures.as_completed(futures):
            if future.result():
                happy_ticket_count += 1

    return happy_ticket_count


if __name__ == "__main__":
    ticket_length = 6
    happy_tickets = count_tickets(ticket_length)
    print(f"Кількість щасливих білетів з {ticket_length} цифрами: {happy_tickets}")
