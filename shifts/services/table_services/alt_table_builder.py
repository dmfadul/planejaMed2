def build_alt_table_data():
    # split in subfunctions
    days = [
        {
            "label": "SÁBADO",
            "number": 1,
            "is_weekend": True,
        },
        {
            "label": "DOMINGO",
            "number": 1,
            "is_weekend": True,
        },
        {
            "label": "SEGUNDA",
            "number": 1,
            "is_weekend": False,
        },
        {
            "label": "TERÇA",
            "number": 1,
            "is_weekend": False,
        },
        {
            "label": "QUARTA",
            "number": 1,
            "is_weekend": False,
        },
        {
            "label": "QUINTA",
            "number": 1,
            "is_weekend": False,
        },
        {
            "label": "SEXTA",
            "number": 1,
            "is_weekend": False,
        },
    ]

    schedule_rows = [
        {
            "index": 1,
            "days": [
                {"code": "CCG", "name": "Vinicius"},
                {"code": "CCG", "name": "Nikolas"},
                {"code": "CCG", "name": "Fabiola"},
                {"code": "CCG", "name": "Camila"},
                {"code": "CCG", "name": "Bruna"},
                {"code": "CCG", "name": "Alberto"},
                {"code": "CCG", "name": "Felipe Bredow"},
            ],
        },
        {
            "index": 2,
            "days": [
                {"code": "CCG", "name": "Augustus"},
                {"code": "CCG", "name": "Rafaella"},
                {"code": "CCG", "name": "Luiza"},
                {"code": "CCG", "name": "Carolina"},
                {"code": "CCG", "name": "Carolina"},
                {"code": "CCG", "name": "Augustus"},
                {"code": "CCG", "name": "Gabriela"},
            ],
        },
        {
            "index": 3,
            "days": [
                {"code": "CCG", "name": "Carolina"},
                {"code": "CCG", "name": "Luiza Silva"},
                {"code": "CCG", "name": "William"},
                {"code": "CCG", "name": "Fabio"},
                {"code": "CCG", "name": "Fabiola"},
                {"code": "CCG", "name": "Carolina"},
                {"code": "CCG", "name": "Heloisa"},
            ],
        },
        {
            "index": 4,
            "days": [
                {"code": "CCG", "name": "William"},
                {"code": "CCG", "name": ""},
                {"code": "CCG", "name": ""},
                {"code": "CCG", "name": "Felype"},
                {"code": "CCG", "name": "Jaaziel"},
                {"code": "CCG", "name": "Fabiola"},
                {"code": "CCG", "name": "João"},
            ],
        },
    ]

    context = {
        "hospital_name": "HOSPITAL UNIVERSITÁRIO EVANGÉLICO MACKENZIE",
        "group_name": "GRUPO DE ANESTESIA MACKENZIE - CCG",
        "days": days,
        "schedule_rows": schedule_rows,
    }

    return context