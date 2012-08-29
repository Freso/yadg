# coding=utf-8

from django.test import TestCase
from scraper import audiojelly, beatport, discogs, itunes, junodownload, metalarchives, musicbrainz

class DiscogsTest(TestCase):
    def test_simple_album(self):
        expected = {'style': ['Goth Rock', 'Synth-pop'], 'title': u'Hast Du Mich Vermisst?', 'country': 'Germany',
                    'format': 'CD, Album', 'label': [u'Richterskala'], 'released': '03 Nov 2000',
                    'catalog': [u'TRI 070 CD'], 'discs': {
                1: [('1', [], 'Schwarzer Schmetterling', '4:50'), ('2', [], 'Where Do The Gods Go', '3:46'),
                    ('3', [], 'Dancing', '5:45'), ('4', [], u'K\xfcss Mich', '5:11'), ('5', [], 'Sing Child', '3:59'),
                    ('6', [], 'Teach Me War', '3:45'), ('7', [], 'Imbecile Anthem', '3:42'),
                    ('8', [], 'Und Wir Tanzten (Ungeschickte Liebesbriefe)', '5:05'), ('9', [], 'Blinded', '7:23')]},
                    'link': 'http://www.discogs.com/ASP-Hast-Du-Mich-Vermisst/release/453432',
                    'artists': [{'type': 'Main', 'name': 'ASP'}], 'genre': ['Electronic', 'Rock']}

        r = discogs.Release.release_from_url('http://www.discogs.com/ASP-Hast-Du-Mich-Vermisst/release/453432')

        self.assertEqual(expected, r.data)

    def test_multiple_cds(self):
        expected = {'style': ['Acoustic', 'Goth Rock', 'Classical', 'Speech'],
                    'title': u"The 'Once In A Lifetime' Recollection Box", 'country': 'Germany',
                    'format': u'4 \xd7 CD, Compilation, Limited Edition, Digipak Box Set, Limited Edition, Hand-Numbered'
            , 'label': [u'[Trisol] Music Group GmbH'], 'released': '25 May 2007', 'catalog': [u'TRI 303 CD'], 'discs': {
                1: [('1', [], 'Once In A Lifetime, Part 1', '5:51'), ('2', [], "A Dead Man's Song", '5:12'),
                    ('3', [], 'Versuchung', '5:45'), ('4', [], 'Torn', '5:04'), ('5', [], 'Demon Love', '4:32'),
                    ('6', [], 'The Paperhearted Ghost', '4:43'), ('7', [], 'A Tale Of Real Love', '5:16'),
                    ('8', [], 'Hunger', '4:49'), ('9', [], 'The Truth About Snow-White', '4:00'),
                    ('10', [], 'She Wore Shadows', '4:35'),
                    ('11', [], 'Und Wir Tanzten (Ungeschickte Liebesbriefe)', '5:17'),
                    ('12', [], 'Once In A Lifetime, Part 2 (Reprise)', '2:44')],
                2: [('1', [], u'K\xfcss Mich', '6:24'), ('2', [], 'Silence - Release', '3:45'),
                    ('3', [], 'Solitude', '3:40'), ('4', [], 'Die Ballade Von Der Erweckung', '8:47'),
                    ('5', [], 'Another Conversation', '3:21'), ('6', [], 'Sing Child', '7:29'),
                    ('7', [], 'Ich Will Brennen', '5:00'), ('8', [], 'Toscana', '6:14'), ('9', [], 'Ride On', '3:42'),
                    ('10', [], 'Hometown', '3:01'), ('11', [], 'Werben', '4:53'),
                    ('12', [], 'Once In A Lifetime, Part 3 (Finale)', '10:08')],
                3: [('1', [], u'H\xe4sslich', '2:25'), ('2', [], 'Backstage (All Areas)', '9:33'),
                    ('3', [], u'Paracetamoltr\xe4ume', '8:37'),
                    ('4', [], u'Ausszug Aus "Tremendista" Feat. Ralph M\xfcller/Gitarre', '24:33'),
                    ('5', [], 'Campari O', '2:39')],
                4: [('1', [], 'Asp, Soundcheck-Outtake: "Sicamore Trees"', '1:34'), ('2', [], 'Demon Love', '4:35'),
                    ('3', [], 'The Truth About Snow-White', '4:34'), ('4', [], 'She Wore Shadows', '5:19'),
                    ('5', [], 'Sing Child', '7:49'), ('6', [], 'Hometown', '3:41'), ('7', [], 'Hunger', '4:34'),
                    ('8', [], 'Silence-Release', '3:28'),
                    ('9', [], 'Asp, Soundcheck-Outtake: "She Moved Through The Fair"', '2:00')]},
                    'link': 'http://www.discogs.com/ASP-Chamber-The-Once-In-A-Lifetime-Recollection-Box/release/977684',
                    'artists': [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                    'genre': ['Classical', 'Non-Music', 'Rock']}

        r = discogs.Release.release_from_url(
            'http://www.discogs.com/ASP-Chamber-The-Once-In-A-Lifetime-Recollection-Box/release/977684')

        self.assertEqual(expected, r.data)

    def test_featuring_track_artist(self):
        expected = {'style': ['Dancehall'], 'title': u'Unter Freunden', 'country': 'Europe', 'format': 'CD, Album',
                    'label': [u'Rootdown Records'], 'released': '01 Apr 2011', 'catalog': [u'RDM13074-2'], 'discs': {
                1: [('1', [], 'Intro', '0:13'), ('2', [], 'Unter Freunden', '3:04'),
                    ('3', [{'type': 'Feature', 'name': "Ce'cile"}], 'Karma', '3:09'),
                    ('4', [], 'Zeit Steht Still', '4:20'), ('5', [], 'Komplizen', '3:05'),
                    ('6', [{'type': 'Feature', 'name': 'Gentleman'}], 'Wenn Sich Der Nebel Verzieht', '3:17'),
                    ('7', [], 'Schwerelos', '3:47'), ('8', [], 'Ein Paar Meter', '3:18'), ('9', [], 'Cash', '3:08'),
                    ('10', [], 'Dezibel', '4:30'), ('11', [], 'Kontrast', '3:34'),
                    ('12', [], u'R\xfcckkehr Der Clowns', '3:18'), ('13', [], 'Superstar', '3:47'),
                    ('14', [], 'Underground', '3:24'),
                    ('15', [{'type': 'Feature', 'name': 'Rebellion'}], 'Showdown', '4:21')]},
                    'link': 'http://www.discogs.com/Mono-Nikitaman-Unter-Freunden/release/3432154',
                    'artists': [{'type': 'Main', 'name': 'Mono & Nikitaman'}], 'genre': ['Reggae']}

        r = discogs.Release.release_from_url('http://www.discogs.com/Mono-Nikitaman-Unter-Freunden/release/3432154')

        self.assertEqual(expected, r.data)

    def test_remix_track_artist(self):
        expected = {'style': ['Alternative Rock'], 'title': u'Aus Der Tiefe', 'country': 'Germany',
                    'format': 'CD, Album, Limited Edition, Digibook CD, Compilation, Limited Edition',
                    'label': [u'[Trisol] Music Group GmbH'], 'released': '01 Jul 2005', 'catalog': [u'TRI 231 CD'],
                    'discs': {1: [('1', [], u'Beschw\xf6rung', '6:31'), ('2', [], u'Willkommen Zur\xfcck', '2:17'),
                        ('3', [], 'Schwarzes Blut', '3:32'), ('4', [], 'Im Dunklen Turm', '1:41'),
                        ('5', [], 'Me', '4:38'), ('6', [], 'Schattenschreie', '0:21'), ('7', [], 'Hunger', '5:21'),
                        ('8', [], 'Fremde Erinnerungen', '1:12'), ('9', [], 'Ballade Von Der Erweckung', '8:53'),
                        ('10', [], 'Tiefenrausch', '4:05'), ('11', [], 'Schmetterling, Du Kleines Ding', '0:42'),
                        ('12', [], 'Ich Komm Dich Holn', '4:17'), ('13', [], 'Werben', '4:28'),
                        ('14', [], 'Aus Der Tiefe', '3:18'), ('15', [], 'Spiegelaugen', '3:24'),
                        ('16', [], 'Tiefenrausch (Reprise)', '1:07'), ('17', [], 'Panik', '4:12'),
                        ('18', [], 'Spiegel', '5:31')], 2: [('1', [], 'Schwarzes Blut (Haltung Version)', '4:09'),
                        ('2', [], 'Werben (Subtil Edit)', '4:17'), ('3', [], 'Me (Single Version)', '3:45'),
                        ('4', [{'type': 'Feature', 'name': 'Sara Noxx'}], 'Tiefenrausch (Feat. Sara Noxx)', '4:05'),
                        ('5', [], 'Hunger (Single Mix)', '4:19'), ('6', [], 'Panik (Ganz Rauf-Verison)', '4:33'),
                        ('7', [], u'Beschw\xf6rung (Siegeszug Instrumental)', '3:25'),
                        ('8', [], 'Buch Des Vergessens (Unreines Spiegelsonett)', '1:55'), (
                            '9', [{'type': 'Remixer', 'name': 'Umbra Et Imago'}],
                            'Kokon (Brandneu-Remix Von Umbra Et Imago)', '4:39'), (
                            '10', [{'type': 'Remixer', 'name': 'Blutengel'}], 'Me (Me And You Remix Von Blutengel)',
                            '5:44')
                        , ('11', [], 'Und Wir Tanzten (Ungeschickte Liebesbriefe) (Live)', '5:47'),
                        ('12', [], 'Ich Will Brennen (Live)', '6:09'),
                        ('13', [], 'Starfucker: In Der Folterkammer', '2:07')]},
                    'link': 'http://www.discogs.com/ASP-Aus-Der-Tiefe-Der-Schwarze-Schmetterling-IV/release/710517',
                    'artists': [{'type': 'Main', 'name': 'ASP'}], 'genre': ['Electronic', 'Rock']}

        r = discogs.Release.release_from_url(
            'http://www.discogs.com/ASP-Aus-Der-Tiefe-Der-Schwarze-Schmetterling-IV/release/710517')

        self.assertEqual(expected, r.data)

    def test_vinyl(self):
        expected = {'style': ['Dancehall', 'Reggae-Pop'], 'title': u'Ausser Kontrolle', 'country': 'Germany',
                    'format': u'2 \xd7 Vinyl, LP', 'label': [u'Rootdown Records'], 'released': '2008',
                    'catalog': [u'RDM 13051-1'], 'discs': {
                1: [('A1', [], 'Intro', None), ('A2', [], 'Schlag Alarm', None),
                    ('A3', [], 'Kann Ja Mal Passieren', None), ('A4', [], 'Ausser Kontrolle', None),
                    ('A5', [], "Hol's Dir", None), ('B1', [], 'Das Alles', None), ('B2', [], 'Digge Digge', None),
                    ('B3', [], 'Nur So', None), ('B4', [], 'Yeah', None),
                    ('C1', [{'type': 'Feature', 'name': 'Russkaja'}], 'Von Osten Bis Westen', None),
                    ('C2', [], 'Wenn Ihr Schlaft', None), ('C3', [], 'Unterwegs', None), ('C4', [], 'Tiktak', None),
                    ('D1', [{'type': 'Feature', 'name': 'Nosliw'}], 'Tut Mir Leid', None),
                    ('D2', [], 'Es Kommt Anders', None),
                    ('D3', [{'type': 'Remixer', 'name': 'Zion Train'}], 'Das Alles (Zion Train Remix)', None)]},
                    'link': 'http://www.discogs.com/Mono-Nikitaman-Ausser-Kontrolle/release/1540929',
                    'artists': [{'type': 'Main', 'name': 'Mono & Nikitaman'}], 'genre': ['Reggae']}

        r = discogs.Release.release_from_url('http://www.discogs.com/Mono-Nikitaman-Ausser-Kontrolle/release/1540929')

        self.assertEqual(expected, r.data)

    def test_featuring_main_artist(self):
        expected = {'style': ['Trance'], 'title': u'In My Dreams', 'country': 'Germany',
                    'format': u'3 \xd7 File, MP3, 320 kbps', 'label': [u'Redux Recordings'], 'released': '08 Feb 2011',
                    'catalog': [u'RDX062'], 'discs': {1: [('1', [], 'In My Dreams (Original Vocal Mix)', '9:18'),
                ('2', [], 'In My Dreams (Original Dub Mix)', '9:18'), (
                    '2', [{'type': 'Remixer', 'name': 'Ost & Meyer'}], 'In My Dreams (Ost & Meyer Extraodinary Mix)',
                    '7:52')]},
                    'link': 'http://www.discogs.com/Lifted-Emotion-feat-Anastasiia-Purple-In-My-Dreams/release/2806179',
                    'artists': [{'type': 'Main', 'name': 'Lifted Emotion'},
                            {'type': 'Feature', 'name': 'Anastasiia Purple'}], 'genre': ['Electronic']}

        r = discogs.Release.release_from_url(
            'http://www.discogs.com/Lifted-Emotion-feat-Anastasiia-Purple-In-My-Dreams/release/2806179')

        self.assertEqual(expected, r.data)

    def test_various_artists(self):
        expected = {'style': ['EBM', 'Darkwave', 'Industrial', 'Goth Rock', 'Electro'], 'title': u'Gothic File 14',
                    'country': 'Germany', 'format': 'CD, Compilation', 'label': [u'Batbeliever Releases'],
                    'released': '2010', 'catalog': [u'BAT 075'], 'discs': {
                1: [('1', [{'type': 'Main', 'name': 'Diary Of Dreams'}], 'Echo In Me', '3:56'),
                    ('2', [{'type': 'Main', 'name': 'Gothminister'}], 'Liar (Version)', '3:39'),
                    ('3', [{'type': 'Main', 'name': 'Sirenia'}], 'The End Of It All (Edit)', '3:57'),
                    ('4', [{'type': 'Main', 'name': 'Merciful Nuns'}], 'Sanctuary', '3:59'),
                    ('5', [{'type': 'Main', 'name': 'Covenant'}], 'Worlds Collide (Demo Version)', '4:21'),
                    ('6', [{'type': 'Main', 'name': 'Ien Oblique'}], 'Drowning World', '4:13'),
                    ('7', [{'type': 'Main', 'name': 'Betamorphose'}], 'In The Name Of God', '4:57'),
                    ('8', [{'type': 'Main', 'name': 'Don Harris'}], 'PsychoCop (Folge 8)', '2:51')]},
                    'link': 'http://www.discogs.com/Various-Gothic-File-14/release/3700493',
                    'artists': [{'type': 'Main', 'name': 'Various'}], 'genre': ['Electronic', 'Rock']}

        r = discogs.Release.release_from_url('http://www.discogs.com/Various-Gothic-File-14/release/3700493')

        self.assertEqual(expected, r.data)