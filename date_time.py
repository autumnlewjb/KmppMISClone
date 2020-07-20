from datetime import datetime

malay = {
    'Sun': 'AHAD',
    'Mon': 'ISNIN',
    'Tue': 'SELASA',
    'Wed': 'RABU',
    'Thu': 'KHAMIS',
    'Fri': 'JUMAAT',
    'Sat': 'SABTU',
}


def get_datetime():
    raw = datetime.now()

    time = raw.strftime("%I:%M %p")
    date = raw.strftime("%B %d, %Y")
    day = raw.strftime("%a")

    return (dict(date=date, time=time, day=malay[day]))


if __name__ == '__main__':
    print(get_datetime())
