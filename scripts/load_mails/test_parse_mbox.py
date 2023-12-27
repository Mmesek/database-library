import datetime

from parse_mbox import parse_mail


def test_parse_mail():
    assert parse_mail(
        {
            "subject": "Bazar - zarezerwowano =?utf-8?Q?Twoj=C4=85_gr=C4=99?= Monster Sanctuary za 7,00 =?utf-8?Q?z=C5=82?=",
            "date": "Wed, 30 Nov 2022 20:11:00 +0100",
            "from": "Bazar <bazar@lowcygier.pl>",
        }
    ) == (
        datetime.datetime(2022, 11, 30, 20, 11, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))),
        "Monster Sanctuary",
        "7.00",
    )
    assert parse_mail(
        {
            "subject": "Bazar - zarezerwowano =?utf-8?Q?Twoj=C4=85_gr=C4=99?= A Plague\n Tale: Innocence za 15,00 =?utf-8?Q?z=C5=82?=",
            "date": "Wed, 30 Oct 2022 20:11:00 +0100",
            "from": "Bazar <bazar@lowcygier.pl>",
        }
    ) == (
        datetime.datetime(2022, 10, 30, 20, 11, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))),
        "A Plague Tale: Innocence",
        "15.00",
    )
    assert parse_mail({"from": "", "subject": "", "date": "Wed, 30 Oct 2022 20:11:00 +0100"}) == None
    assert (
        parse_mail({"from": "test <test@test.test>", "subject": "test", "date": "Wed, 30 Oct 2022 20:11:00 +0100"})
        == None
    )
    assert (
        parse_mail(
            {"from": "test <test@test.test>", "subject": "zarezerwowano", "date": "Wed, 30 Oct 2022 20:11:00 +0100"}
        )
        == None
    )
    assert (
        parse_mail(
            {
                "from": "Bazar <bazar@lowcygier.pl>",
                "subject": "test",
                "date": "Wed, 30 Oct 2022 20:11:00 +0100",
            }
        )
        == None
    )
