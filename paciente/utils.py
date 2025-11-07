# perfis/utils.py
import datetime
from calendar import HTMLCalendar

class PacienteCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(PacienteCalendar, self).__init__()
        self.setfirstweekday(6) # Começa a semana no Domingo

    # Formata um dia como uma <td> clicável
    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="day-disabled"></td>' # Dia fora do mês

        data_iso = f"{self.year}-{self.month:02d}-{day:02d}"

        # Desabilita dias no passado
        if datetime.date(self.year, self.month, day) < datetime.date.today():
             return f'<td class="day-disabled">{day}</td>'

        # Este é um dia válido e clicável
        return f'<td class="day-cell" data-date="{data_iso}">{day}</td>'

    # Formata o mês como <table> com classes CSS
    def formatmonth(self, withyear=True):
        cal = super().formatmonth(self.year, self.month)
        cal = cal.replace(
            '<table border="0" cellpadding="0" cellspacing="0" class="month">',
            '<table class="calendar-table">'
        )
        cal = cal.replace('<th>', '<th class="calendar-header">')
        return cal