# coding=utf-8

from django.test import TestCase
from scraper import audiojelly, beatport, discogs, itunes, junodownload, metalarchives, musicbrainz

class DiscogsTest(TestCase):
    maxDiff = None

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

    def test_label_with_suffix(self):
        expected = {'style': ['Medieval'], 'title': u'Prima Nocte', 'country': 'Germany', 'format': 'CD, Album',
                    'label': [u'Indigo'], 'released': '25 Nov 2005', 'catalog': [u'CD 55182'], 'discs': {
            1: [('1', [], 'Es War Einmal', '2:52'), ('2', [], 'Das Mittelalter', '4:20'), ('3', [], 'Drachentanz', '3:44'),
                ('4', [], 'Das Turnier', '4:14'), ('5', [], 'Prima Nocte', '5:31'), ('6', [], u'B\xe4rentanz', '3:52'),
                ('7', [], 'Herren Der Winde', '4:25'), ('8', [], 'Der Teufel', '4:50'), ('9', [], 'Schneewittchen', '6:17'),
                ('10', [], 'Der Traum', '5:19'), ('11', [], u'R\xe4uber', '3:26'), ('12', [], 'Sauflied', '3:54'),
                ('13', [], 'Teufelsgeschenk', '4:24'), ('14', [], u'La\xdft Die Ritter Schlafen', '5:13'),
                ('15', [], 'Gute Nacht', '7:00')]},
                    'link': 'http://www.discogs.com/Feuerschwanz-Prima-Nocte/release/2611694',
                    'artists': [{'type': 'Main', 'name': 'Feuerschwanz'}],
                    'genre': ['Folk', 'World', 'Country', 'Rock']}

        r = discogs.Release.release_from_url('http://www.discogs.com/Feuerschwanz-Prima-Nocte/release/2611694')

        self.assertEqual(expected, r.data)

    def test_404(self):
        r = discogs.Release.release_from_url('http://www.discogs.com/Various-Gothic-File-14/release/999999999')
        try:
            r.data
            self.assertFalse(True)
        except discogs.DiscogsAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e


class MusicbrainzTest(TestCase):
    maxDiff = None

    def test_simple_album(self):
        expected = {'title': 'Hast Du mich vermisst? Der schwarze Schmetterling, Teil I', 'country': 'Germany',
                    'format': 'CD, Album', 'label': ['Trisol'], 'released': '2004-09-23', 'catalog': ['TRI 070 CD'],
                    'discs': {1: [('1', [], 'Intro: In meiner Vorstellung', '4:34'),
                        ('2', [], 'Schwarzer Schmetterling', '4:50'), ('3', [], 'Where Do the Gods Go', '3:46'),
                        ('4', [], 'Dancing', '5:45'), ('5', [], u'K\xfcss mich', '5:11'),
                        ('6', [], 'Sing Child', '3:58'), ('7', [], 'Teach Me War', '3:45'),
                        ('8', [], 'Imbecile Anthem', '3:42'),
                        ('9', [], 'Und wir tanzten (Ungeschickte Liebesbriefe)', '5:04'), ('10', [], 'Blinded', '7:24'),
                        ('11', [], 'Where Do the Gods Go (re-unleashed club edit)', '4:39')]},
                    'link': 'http://musicbrainz.org/release/e008606b-a1c9-48ab-8011-5dbf8b874f1b',
                    'artists': [{'type': 'Main', 'name': 'ASP'}]}

        r = musicbrainz.Release.release_from_url('http://musicbrainz.org/release/e008606b-a1c9-48ab-8011-5dbf8b874f1b')

        self.assertEqual(expected, r.data)

    def test_multiple_cds(self):
        expected = {'title': 'Once in a Lifetime', 'country': 'Germany', 'format': u'4\xd7CD, Album + Live',
                    'label': ['Trisol'], 'released': '2007-05-25', 'catalog': ['TRI 303 CD'],
                    'discs': {1: [('1', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Once in a Lifetime, Part 1', '5:51'),
                        ('2', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                         u'A Dead Man\u2019s Song', '5:12'),
                        ('3', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}], 'Versuchung',
                         '5:45'),
                        ('4', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}], 'Torn', '5:04'),
                        ('5', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}], 'Demon Love',
                         '4:32'),
                        ('6', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                         'The Paperhearted Ghost', '4:43'),
                        ('7', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                         'A Tale of Real Love', '5:16'),
                        ('8', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}], 'Hunger', '4:49'),
                        ('9', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                         'The Truth About Snow-White', '4:00'),
                        (
                            '10', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                            'She Wore Shadows'
                            , '4:36'),
                        ('11', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                         'Und wir tanzten (Ungeschickte Liebesbriefe)', '5:17'),
                        ('12', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                         'Once in a Lifetime, Part 2 (reprise)', '2:44')],
                              2: [('1', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   u'K\xfcss mich', '6:24'),
                                  ('2', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Silence - Release', '3:45'),
                                  ('3', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Solitude', '3:40'),
                                  ('4', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Die Ballade von der Erweckung', '8:47'),
                                  ('5', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Another Conversation', '3:21'),
                                  ('6', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Sing Child', '7:29'),
                                  ('7', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Ich will brennen', '5:00'),
                                  (
                                      '8', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                      'Toscana'
                                      , '6:14'),
                                  (
                                      '9', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                      'Ride On'
                                      , '3:42'),
                                  ('10', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Hometown', '3:01'),
                                  (
                                      '11', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                      'Werben'
                                      , '4:53'),
                                  ('12', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Once in a Lifetime, Part 3 (Finale)', '10:08')],
                              3: [('1', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   u'H\xe4sslich', '2:25'),
                                  ('2', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Backstage (All Areas)', '9:33'),
                                  ('3', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   u'Paracetamoltr\xe4ume', '8:37'),
                                  ('4', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'},
                                          {'type': 'Feature', 'name': u'Ralph M\xfcller'}],
                                   u'Auszug aus \u201eTremendista\u201c', '24:33'),
                                  ('5', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Campari O', '2:39')],
                              4: [('1', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Sicamore Trees (ASP soundcheck out-take)', '1:34'),
                                  ('2', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Demon Love', '4:35'),
                                  ('3', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'The Truth About Snow-White', '4:35'),
                                  ('4', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'She Wore Shadows', '5:19'),
                                  ('5', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Sing Child', '7:49'),
                                  ('6', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Hometown', '3:41'),
                                  (
                                      '7', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                      'Hunger',
                                      '4:34'),
                                  ('8', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'Silence - Release', '3:28'),
                                  ('9', [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}],
                                   'She Moved Through the Fair (ASP soundcheck out-take)', '2:00')]},
                    'link': 'http://musicbrainz.org/release/79de4a0c-b469-4dfd-b23c-129462b741fb',
                    'artists': [{'type': 'Main', 'name': 'ASP'}, {'type': 'Main', 'name': 'Chamber'}]}

        r = musicbrainz.Release.release_from_url('http://musicbrainz.org/release/79de4a0c-b469-4dfd-b23c-129462b741fb')

        self.assertEqual(expected, r.data)

    def test_various_artists(self):
        expected = {'title': 'Gothic File 11', 'country': 'Germany', 'format': 'CD, Album + Compilation',
                    'label': ['Batbeliever Releases'], 'released': '2010', 'catalog': ['BAT 065'], 'discs': {
                1: [('1', [{'type': 'Main', 'name': 'Spectra Paris'}], 'Carrie Satan', '5:12'),
                    ('2', [{'type': 'Main', 'name': 'Absurd Minds'}], 'Countdown', '4:13'),
                    ('3', [{'type': 'Main', 'name': 'Nachtmahr'}], u'M\xe4dchen in Uniform (Faderhead remix)', '3:53'),
                    ('4', [{'type': 'Main', 'name': 'Noisuf-X'}], 'Fucking Invective', '4:33'),
                    ('5', [{'type': 'Main', 'name': ':wumpscut:'}], 'Loyal to My Hate (Solar Fake remix)', '4:24'),
                    ('6', [{'type': 'Main', 'name': 'KiEw'}], 'Melancholie (382edit)', '3:52'),
                    ('7', [{'type': 'Main', 'name': 'Mantus'}], 'Gegen die Welt', '4:47'),
                    ('8', [{'type': 'Main', 'name': 'Oomph!'}], "Ready or Not (I'm Coming)", '3:22'),
                    ('9', [{'type': 'Main', 'name': 'Rob Zombie'}], 'What?', '2:46'),
                    ('10', [{'type': 'Main', 'name': 'Megaherz'}], 'Ebenbild (Die Krupps remix)', '5:43'),
                    ('11', [{'type': 'Main', 'name': 'Eisbrecher'}], 'Vergissmeinnicht (live)', '3:59'),
                    ('12', [{'type': 'Main', 'name': 'Zeromancer'}], 'Industrypeople', '4:14'),
                    ('13', [{'type': 'Main', 'name': 'Julien-K'}], 'Kick the Bass', '3:42'),
                    ('14', [{'type': 'Main', 'name': 'Nosferatu'}], 'Black Hole', '5:25'),
                    ('15', [{'type': 'Main', 'name': 'Die Art'}], 'Swimming in Dirty Water', '4:24'),
                    ('16', [{'type': 'Main', 'name': 'Mad Sin'}], 'Wreckhouse Stomp', '3:04')]},
                    'link': 'http://musicbrainz.org/release/9d78a55c-0eee-4b61-b6eb-b69765c37740',
                    'artists': [{'type': 'Main', 'name': 'Various'}]}

        r = musicbrainz.Release.release_from_url('http://musicbrainz.org/release/9d78a55c-0eee-4b61-b6eb-b69765c37740')

        self.assertEqual(expected, r.data)

    def test_disc_titles(self):
        expected = {'title': 'Original Album Classics', 'country': 'Europe', 'format': u'5\xd7CD, Album + Compilation',
                    'label': ['Epic'],
                    'discTitles': {1: u'The Brothers: Isley', 2: u'Get Into Something', 3: u"Givin' It Back",
                                   4: u'Brother, Brother, Brother', 5: u'3 + 3'}, 'released': '2008',
                    'catalog': ['88697304842'], 'discs': {
                1: [('1', [], 'I Turned You On', '2:38'), ('2', [], 'Vacuum Cleaner', '2:56'),
                    ('3', [], 'I Got to Get Myself Together', '3:38'), ('4', [], 'Was It Good to You?', '2:44'),
                    ('5', [], 'The Blacker the Berry (a.k.a. Black Berries)', '5:53'),
                    ('6', [], 'My Little Girl', '3:41'), ('7', [], 'Get Down Off of the Train', '3:12'),
                    ('8', [], 'Holding On', '2:36'), ('9', [], 'Feels Like the World', '3:26')],
                2: [('1', [], 'Get Into Something', '7:30'), ('2', [], 'Freedom', '3:38'),
                    ('3', [], 'Take Inventory', '2:47'), ('4', [], "Keep on Doin'", '4:02'),
                    ('5', [], 'Girls Will Be Girls', '2:51'), ('6', [], 'I Need You So', '4:25'),
                    ('7', [], 'If He Can You Can', '3:45'), ('8', [], 'I Got to Find Me One', '4:38'),
                    ('9', [], 'Beautiful', '3:06'), ('10', [], 'Bless Your Heart', '3:03')],
                3: [('1', [], 'Ohio - Machine Gun', '9:14'), ('2', [], 'Fire and Rain', '5:29'),
                    ('3', [], 'Lay Lady Lay', '10:22'), ('4', [], 'Spill the Wine', '6:32'),
                    ('5', [], 'Nothing to Do But Today', '3:39'), ('6', [], 'Cold Bologna', '2:59'),
                    ('7', [], "Love the One You're With", '3:39')],
                4: [('1', [], 'Brother, Brother', '3:17'), ('2', [], 'Put A Little Love In Your Heart', '3:02'),
                    ('3', [], "Sweet Season / Keep On Walkin'", '5:13'), ('4', [], 'Work To Do', '3:12'),
                    ('5', [], 'Pop That Thang', '2:54'), ('6', [], 'Lay Away', '3:23'),
                    ('7', [], "It's Too Late", '10:31'), ('8', [], 'Love Put Me On The Corner', '6:30')],
                5: [('1', [], 'That Lady, Parts 1 & 2', '5:35'), ('2', [], "Don't Let Me Be Lonely Tonight", '3:59'),
                    ('3', [], 'If You Were There', '3:23'), ('4', [], 'You Walk Your Way', '3:06'),
                    ('5', [], 'Listen to the Music', '4:06'), ('6', [], 'What It Comes Down To', '3:54'),
                    ('7', [], 'Sunshine (Go Away Today)', '4:22'), ('8', [], 'Summer Breeze', '6:12'),
                    ('9', [], 'The Highways of My Life', '4:53'), ('10', [], 'That Lady (live)', '3:42')]},
                    'link': 'http://musicbrainz.org/release/12c94a0f-828f-4ab3-8e0d-dfe4599dc310',
                    'artists': [{'type': 'Main', 'name': 'The Isley Brothers'}]}

        r = musicbrainz.Release.release_from_url('http://musicbrainz.org/release/12c94a0f-828f-4ab3-8e0d-dfe4599dc310')

        self.assertEqual(expected, r.data)

    def test_special_sub_heading(self):
        expected = {'title': 'Fremder-Zyklus, Teil 1.1: Die GeistErfahrer', 'country': 'Germany',
                    'format': u'2\xd7CD, EP', 'label': ['Trisol'], 'discTitles': {2: u'Bonus CD'},
                    'released': '2012-11-16', 'catalog': ['TRI 460 CD'], 'discs': {
            1: [('1', [], 'GeistErfahrer', '6:00'), ('2', [], 'In Sack und Asche', '7:20'),
                ('3', [], u'\xdcberH\xe4rte', '6:16'), ('4', [], 'Carpe noctem', '5:12'),
                ('5', [], 'Weichen(t)stellung (GeistErfahrer Reprise)', '4:34'), ('6', [], 'Danach', '8:36')],
            2: [('1', [], 'Sing Child', '6:44'), ('2', [], 'Duett (Minnelied der Incubi)', '4:11'),
                ('3', [], 'Krabat', '5:58'), ('4', [], 'Unverwandt', '11:07'), ('5', [], 'Werben', '7:20')]},
                    'link': 'http://musicbrainz.org/release/fc6ee7a8-c70a-4c8f-ab42-43a457a0731f',
                    'artists': [{'type': 'Main', 'name': 'ASP'}]}

        r = musicbrainz.Release.release_from_url('http://musicbrainz.org/release/fc6ee7a8-c70a-4c8f-ab42-43a457a0731f')

        self.assertEqual(expected, r.data)

    def test_404(self):
        r = musicbrainz.Release.release_from_url('http://musicbrainz.org/release/12345-abcdefg')
        try:
            r.data
            self.assertFalse(True)
        except musicbrainz.MusicBrainzAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e


class BeatportTest(TestCase):
    maxDiff = None

    def test_simple_album(self):
        expected = {'title': u'Love Love Love Yeah', 'label': [u'Playhouse'], 'released': u'2007-01-22',
                    'catalog': [u'PLAY131'], 'discs': {
                1: [('1', [], u'Love Love Love Yeah', u'07:55'), ('2', [], u'Bus Driver', u'03:07'),
                    ('3', [], u'Christiane', u'00:24'), ('4', [], u'So Cold', u'03:32')]},
                    'link': 'http://www.beatport.com/release/love-love-love-yeah/43577',
                    'artists': [{'type': 'Main', 'name': u'Rework'}], 'genre': [u'Electro House', u'DJ Tools']}

        r = beatport.Release.release_from_url('http://www.beatport.com/release/love-love-love-yeah/43577')

        self.assertEqual(expected, r.data)

    def test_remix_track_artist(self):
        expected = {'title': u'Love Spy / Love Dies', 'label': [u'Karatemusik'], 'released': u'2006-04-19',
                    'catalog': [u'KM013'], 'discs': {1: [(
                '1', [{'type': 'Remixer', 'name': u'Error Error'}], u'Love Spy / Love Dies [Error Error Remix]',
                u'07:27'),
                ('2', [], u'Love Spy / Love Dies', u'07:07'), ('3', [], u'Reply 23', u'06:58')]},
                    'link': 'http://www.beatport.com/release/love-spy-love-dies/27944',
                    'artists': [{'type': 'Main', 'name': u'Polygamy Boys'}], 'genre': [u'Tech House', u'Electro House']}

        r = beatport.Release.release_from_url('http://www.beatport.com/release/love-spy-love-dies/27944')

        self.assertEqual(expected, r.data)

    def test_various_artists(self):
        expected = {'title': u'DJ Tunes Compilation', 'format': u'Album', 'label': [u'Carlo Cavalli Music Group'],
                    'released': u'2012-01-05', 'catalog': [u'CMG117'], 'discs': {
                1: [('1', [{'type': 'Main', 'name': u'Sam Be-Kay'}], u'Forever Loved', u'5:20'), (
                    '2', [{'type': 'Main', 'name': u'Eros Locatelli'}, {'type': 'Remixer', 'name': u'Alex Faraci'}],
                    u'Sweep [Alex Faraci Remix]', u'6:38'), ('3', [{'type': 'Main', 'name': u'Babette Duwez'},
                        {'type': 'Main', 'name': u'Joel Reichert'}, {'type': 'Remixer', 'name': u'David Ahumada'}],
                                                             u'Humo Y Neon [David Ahumada Remix]', u'4:58'), (
                    '4', [{'type': 'Main', 'name': u'Alex Faraci'}, {'type': 'Remixer', 'name': u'Massimo Russo'}],
                    u'Night Melody [Massimo Russo La Guitarra Remix]', u'6:17'),
                    ('5', [{'type': 'Main', 'name': u'Fingers Clear'}], u'30 m [Original mix]', u'6:33'),
                    ('6', [{'type': 'Main', 'name': u'Erion Gjuzi'}], u'Just Begin', u'7:09'),
                    ('7', [{'type': 'Main', 'name': u'Dany Cohiba'}], u'Achakkar [Original mix]', u'6:28'), (
                        '8',
                        [{'type': 'Main', 'name': u'Massimo Russo'}, {'type': 'Remixer', 'name': u'Italianbeat Guys'}],
                        u'Raveline [Italianbeat Guys Remix]', u'6:46'), (
                        '9', [{'type': 'Main', 'name': u'Jurgen Cecconi'}, {'type': 'Main', 'name': u'Beethoven Tbs'}],
                        u'Grey 2 Fade feat. Babette Duwez [Jurgen Cecconi Mix]', u'10:53'),
                    ('10', [{'type': 'Main', 'name': u'Carlo Cavalli'}], u'Tanzmania', u'7:00')]},
                    'link': 'http://www.beatport.com/release/dj-tunes-compilation/851318',
                    'artists': [{'type': 'Main', 'name': 'Various'}],
                    'genre': [u'Progressive House', u'House', u'Deep House', u'Minimal', u'Tech House']}

        r = beatport.Release.release_from_url('http://www.beatport.com/release/dj-tunes-compilation/851318')

        self.assertEqual(expected, r.data)

    def test_404(self):
        r = beatport.Release.release_from_url('http://www.beatport.com/release/blubb/123')
        try:
            r.data
            self.assertFalse(True)
        except beatport.BeatportAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e


class MetalarchivesTest(TestCase):
    maxDiff = None

    def test_simple_album(self):
        expected = {'title': 'Century Child', 'format': 'Full-length', 'label': ['Spinefarm Records'],
                    'released': 'June 24th, 2002', 'discs': {
                1: [('1', [], 'Bless the Child', '06:12'), ('2', [], 'End of all Hope', '03:55'),
                    ('3', [], 'Dead to the World', '04:20'), ('4', [], 'Ever Dream', '04:44'),
                    ('5', [], 'Slaying the Dreamer', '04:32'), ('6', [], 'Forever Yours', '03:50'),
                    ('7', [], 'Ocean Soul', '04:15'), ('8', [], 'Feel for You', '03:55'),
                    ('9', [], 'The Phantom of the Opera', '04:10'), ('10', [], 'Beauty of the Beast', '10:22')]},
                    'link': 'http://www.metal-archives.com/albums/Nightwish/Century_Child/3719',
                    'artists': [{'type': 'Main', 'name': 'Nightwish'}]}

        r = metalarchives.Release.release_from_url('http://www.metal-archives.com/albums/Nightwish/Century_Child/3719')

        self.assertEqual(expected, r.data)

    def test_multiple_cds(self):
        expected = {'title': 'Black Symphony', 'format': 'Live album', 'label': ['Roadrunner Records'],
                    'released': 'September 22nd, 2008', 'discs': {
                1: [('1', [], 'Ouverture', '07:43'), ('2', [], "Jillian (I'd Give My Heart)", '04:39'),
                    ('3', [], 'The Howling', '06:31'), ('4', [], 'Stand My Ground', '04:33'),
                    ('5', [], 'The Cross', '05:22'), ('6', [], 'What Have You Done?', '04:58'),
                    ('7', [], 'Hand Of Sorrow', '05:40'), ('8', [], 'The Heart Of Everything', '05:48'),
                    ('9', [], 'Forgiven', '04:53'), ('10', [], 'Somewhere', '04:24'),
                    ('11', [], 'The Swan Song', '04:00'), ('12', [], 'Memories', '04:03')],
                2: [('1', [], 'Our Solemn Hour', '05:22'), ('2', [], 'The Other Half (Of Me)', '05:04'),
                    ('3', [], 'Frozen', '06:00'), ('4', [], 'The Promise', '04:32'), ('5', [], 'Angels', '08:15'),
                    ('6', [], 'Mother Earth', '04:02'), ('7', [], 'The Truth Beneath The Rose', '07:23'),
                    ('8', [], 'Deceiver of Fools', '07:38'), ('9', [], 'All I Need', '04:55'),
                    ('10', [], 'Ice Queen', '07:15')]},
                    'link': 'http://www.metal-archives.com/albums/Within_Temptation/Black_Symphony/212779',
                    'artists': [{'type': 'Main', 'name': 'Within Temptation'}]}

        r = metalarchives.Release.release_from_url(
            'http://www.metal-archives.com/albums/Within_Temptation/Black_Symphony/212779')

        self.assertEqual(expected, r.data)

    def test_404(self):
        r = metalarchives.Release.release_from_url(
            'http://www.metal-archives.com/albums/Within_Temptation/Black_Symphony/999999999')
        try:
            r.data
            self.assertFalse(True)
        except metalarchives.MetalarchivesAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e


class AudiojellyTest(TestCase):
    maxDiff = None

    def test_simple_album(self):
        expected = {'title': u'Love \u221a Infinity (Love to the Square Root of Infinity)',
                    'label': ['defamation records'], 'released': '2011-10-27', 'catalog': ['5055506333041'], 'discs': {
                1: [('1', [], u'Love \u221a Infinity (Radio Edit)', '02:49'),
                    ('2', [], u'Love \u221a Infinity (Vocal Club Mix)', '06:46'),
                    ('3', [], u'Love \u221a Infinity (Instrumental Club Mix)', '06:46')]},
                    'link': 'http://www.audiojelly.com/releases/love-infinity-love-to-the-square-root-of-infinity/211079'
            , 'artists': [{'type': 'Main', 'name': 'AudioFreQ'}], 'genre': ['Electro House']}

        r = audiojelly.Release.release_from_url(
            'http://www.audiojelly.com/releases/love-infinity-love-to-the-square-root-of-infinity/211079')

        self.assertEqual(expected, r.data)

    def test_featuring_main_artist(self):
        expected = {'title': 'Where Is Love (Love Is Hard To Find)', 'label': ['Ultra Records'],
                    'released': '2011-10-24', 'catalog': ['UL 2903'], 'discs': {
                1: [('1', [], 'Where Is Love (Love Is Hard To Find) (Lucky Date Remix)', '06:15'),
                    ('2', [], 'Where Is Love (Love Is Hard To Find) (Electrixx Radio Edit)', '03:54'),
                    ('3', [], 'Where Is Love (Love Is Hard To Find) (Electrixx Remix)', '06:07'),
                    ('4', [], 'Where Is Love (Love Is Hard To Find) (Matthew Sterling Remix)', '05:32'),
                    ('5', [], 'Where Is Love (Love Is Hard To Find) (Disco Fries Remix)', '05:51'),
                    ('6', [], 'Where Is Love (Love Is Hard To Find) (Mysto & Pizzi Remix)', '05:28'),
                    ('7', [], 'Where Is Love (Love Is Hard To Find) (Ido Shoam Remix)', '05:01'),
                    ('8', [], 'Where Is Love (Love Is Hard To Find) (SpacePlant Remix)', '06:11')]},
                    'link': 'http://www.audiojelly.com/releases/where-is-love-love-is-hard-to-find/210428',
                    'artists': [{'type': 'Main', 'name': 'Mysto'}, {'type': 'Main', 'name': 'Pizzi'},
                            {'type': 'Feature', 'name': 'Johnny Rose'}], 'genre': ['Electronica']}

        r = audiojelly.Release.release_from_url(
            'http://www.audiojelly.com/releases/where-is-love-love-is-hard-to-find/210428')

        self.assertEqual(expected, r.data)

    def test_various_artists(self):
        expected = {'title': 'Plus Various I', 'label': ['Sound Academy Plus'], 'released': '2012-04-01',
                    'catalog': ['SAP042'], 'discs': {
                1: [('1', [{'type': 'Main', 'name': 'Can Yuksel'}], 'With You Forever (Original Mix)', '07:08'), (
                    '2', [{'type': 'Main', 'name': 'Ismael Casimiro'}, {'type': 'Main', 'name': 'Borja Maneje'}],
                    'Electro Deep (Gokhan Guneyli Remix)', '08:48'),
                    ('3', [{'type': 'Main', 'name': 'Roby B.'}], 'Deal (Original Mix)', '06:45'),
                    ('4', [{'type': 'Main', 'name': 'Serdar Ors'}], 'Musica (Can Yuksel Remix)', '06:11')]},
                    'link': 'http://www.audiojelly.com/releases/plus-various-i/230282',
                    'artists': [{'type': 'Main', 'name': 'Various'}], 'genre': ['Tech House']}

        r = audiojelly.Release.release_from_url('http://www.audiojelly.com/releases/plus-various-i/230282')

        self.assertEqual(expected, r.data)

    def test_404(self):
        r = audiojelly.Release.release_from_url('http://www.audiojelly.com/releases/plus-various-i/999999')
        try:
            r.data
            self.assertFalse(True)
        except audiojelly.AudiojellyAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e


class JunodownloadTest(TestCase):
    maxDiff = None

    def test_simple_album(self):
        expected = {'title': 'Love', 'label': ['3 Beat'], 'released': '3 July, 2011', 'catalog': ['3BEAT 051'],
                    'discs': {1: [('1', [], 'Love (UK radio edit)', '02:31'), ('2', [], 'Love (club mix)', '04:59'),
                        ('3', [], 'Love (eSquire radio edit)', '03:53'), ('4', [], 'Love (eSquire mix)', '05:57'),
                        ('5', [], 'Love (7th Heaven radio edit)', '03:50'), ('6', [], 'Love (7th Heaven mix)', '06:34'),
                        ('7', [], 'Love (Dandeej mix)', '05:15'), ('8', [], 'Love (DJ Andi mix)', '05:41'),
                        ('9', [], 'Love (Klubfiller mix)', '06:35'), ('10', [], 'Love (Klubfiller dub mix)', '06:29')]},
                    'link': 'http://www.junodownload.com/products/love/1774811-02/',
                    'artists': [{'type': 'Main', 'name': 'Inna'}], 'genre': ['Funky', 'Club House']}

        r = junodownload.Release.release_from_url('http://www.junodownload.com/products/love/1774811-02/')

        self.assertEqual(expected, r.data)

    def test_featuring_main_artist(self):
        expected = {'title': 'Love', 'label': ['Staff Productions'], 'released': '12 November, 2010',
                    'catalog': ['SFP 012'], 'discs': {1: [('1', [], 'Love (original Miami mix)', '05:01'),
                ('2', [], "Love (Mustafa's Deep Piano mix)", '05:08'),
                ('3', [], 'Love (D-Malice Afro-edit vocal)', '06:21'),
                ('4', [], 'Love (RY meets Mustafa vocal mix)', '06:05'),
                ('5', [], 'Love (Ospina & Oscar P remix)', '06:05'),
                ('6', [], 'Love (Ospina & Oscar P Drum dub)', '06:05'), ('7', [], 'Love (Steven Stone remix)', '06:29'),
                ('8', [], 'Love (David Mateo & Rafix club mix)', '04:57'),
                ('9', [], 'Love (Rafael Yapudjian Meets RyB remix)', '07:29'),
                ('10', [], 'Love (acoustic mix)', '03:52'),
                ('11', [], 'Love (D-Malice Afro edit instrumental)', '06:21'),
                ('12', [], 'Love (Ospina & Oscar P intru-mental)', '06:05'),
                ('13', [], 'Love (Steven Stone instrumental remix)', '06:28'),
                ('14', [], 'Love (David Mateo & Rafix radio club mix instrumental)', '04:57'),
                ('15', [], 'Love (Rafael Yapudjian Meets RyB dub remix)', '07:29'),
                ('16', [], 'Love (RY Meets Mustafa instrumental mix)', '06:05')]},
                    'link': 'http://www.junodownload.com/products/love/1662955-02/',
                    'artists': [{'type': 'Main', 'name': 'Mustafa'}, {'type': 'Feature', 'name': 'Tasita D mour'}],
                    'genre': ['Broken Beat', 'Nu Jazz', 'Nu Soul']}

        r = junodownload.Release.release_from_url('http://www.junodownload.com/products/love/1662955-02/')

        self.assertEqual(expected, r.data)

    def test_mixed_various_main_artists(self):
        expected = {'title': 'A Love Story 89-10 (unmixed tracks)', 'label': ['Bass Planet Germany'],
                    'released': '21 July, 2010', 'catalog': ['425011 7613280'], 'discs': {
                1: [('1', [], 'Westbam - Official Anthems (continuous DJ mix)', '1:03:00'),
                    ('2', [], 'Westbam - Love Sounds 3000 (continuous DJ mix)', '1:19:27'),
                    ('3', [], 'Westbam - The Original Feelings (continuous DJ mix)', '1:09:03'),
                    ('4', [], "Westbam - Don't Look Back In Anger (short mix)", '03:21'),
                    ('5', [], 'The Love Committee - Love Rules', '06:52'), (
                        '6', [], 'WestBam & The Love Committee - Love Is Everywhere (New Location) (original mix)',
                        '07:19')
                    , ('7', [], 'WestBam & The Love Committee - Highway To Love (Final remix)', '07:40'),
                    ('8', [], 'WestBam & The Love Committee - United States Of Love', '07:01'),
                    ('9', [], 'Dr Motte & Westbam presents - Sunshine', '04:04'),
                    ('10', [], 'Dr Motte & Westbam presents - One World One Future', '03:42'),
                    ('11', [], "The Love Committee - You Can't Stop Us", '06:47'),
                    ('12', [], 'Dr Motte & Westbam presents - Loveparade 2000', '03:28'),
                    ('13', [], 'Dr Motte & Westbam presents - Music Is The Key', '08:19'),
                    ('14', [], "Felix - Don't You Want Me (Hooj mix)", '05:55'),
                    ('15', [], 'Blake Baxter - One More Time', '04:14'),
                    ('16', [], 'The Break Boys - My House Is Your House (Miami Beach Break mix)', '06:20'),
                    ('17', [], 'The Love Committee - We Feel Love', '05:34'),
                    ('18', [], 'Paul & Fritz Kalkbrenner - Sky And Sand (Berlin Calling mix)', '03:59'),
                    ('19', [], 'The Love Committee - Access Peace', '07:11'),
                    ('20', [], 'Westbam - Spoon (unvergesslisch)', '06:59'), ('21', [], 'Westbam - Escalate', '06:27'),
                    ('22', [], 'Deekline & Ed Solo - Handz Up (Stantons Warriors remix Westbam edit)', '04:48'),
                    ('23', [], 'Westbam - Fake Blue Eyes', '04:33'),
                    ('24', [], 'Moguai & Westbam - Original Hardcore EP', '04:48'),
                    ('25', [], 'Jewelz - Get Down', '06:01'),
                    ('26', [], 'Tom Wax & Strobe - Cantate (Lalai Lala) (radio mix)', '03:22'),
                    ('27', [], 'Smash Hifi - Take You Back (VIP edit)', '05:02'),
                    ('28', [], 'Elite Force & Hatiras & JELO & Vandal & Stanton Warriors - MAD', '07:08'),
                    ('29', [], 'Mom & Dad - Judas (Dem Slackers remix)', '04:28'),
                    ('30', [], 'DJ Icey - Yeah Right', '04:57'), ('31', [], 'Westbam - Sage Sage', '04:40'),
                    ('32', [], 'Felix Cartal - Love', '05:14'),
                    ('33', [], 'Westbam - Hard Times (Westbam edit)', '03:45'),
                    ('34', [], 'Deadmau5 - Strobe (Plump DJs remix)', '05:43'),
                    ('35', [], 'Members Of Mayday - Make My Day (short mix)', '03:28'),
                    ('36', [], 'Boris Dlugosch - Bangkok', '05:23'), ('37', [], 'Westbam - Yeah Bla Whatever', '05:55'),
                    ('38', [], 'Elite Force & Daniele Papini & Harnessnoise - Harness The Nonsense', '06:12'),
                    ('39', [], 'Tom De Neef Presents Jacksquad - Boavista', '07:33'),
                    ('40', [], 'Dennis Ferrer - Hey Hey (radio edit)', '03:09'),
                    ('41', [], "Steve Aoki - I'm In The House (feat Zuper Blahq)", '03:19'),
                    ('42', [], 'Peter Licht - Sonnendeck (Deck 5 mix)', '03:20'),
                    ('43', [], 'Orbital - Chime (extended version)', '12:40'),
                    ('44', [], 'Format 1 - Solid Session', '04:21'),
                    ('45', [], 'Fierce Ruling Diva - Rubb It In', '05:05'),
                    ('46', [], 'X-101 - Sonic Destroyer', '05:00'), ('47', [], 'Marusha - Ravechannel', '03:36'),
                    ('48', [], 'DJ Dick - Malefactor', '06:16'), ('49', [], 'Westbam - My Life Of Crime', '05:13'),
                    ('50', [], 'Westbam - Mr Peanut', '05:43'), ('51', [], 'Westbam - Endlos', '21:20'),
                    ('52', [], 'The Nighttripper - Tone Explotation', '05:10'),
                    ('53', [], 'Vein Melter - Hypnotized', '08:41'),
                    ('54', [], 'Dr Mottes Euphorhythm - Patrik', '05:35'),
                    ('55', [], 'Westbam - Super Old School Mix', '10:47'),
                    ('56', [], 'Westbam & Nena - Oldschool Baby (piano mix)', '05:58'),
                    ('57', [], 'Richie Rich - Salsa House', '06:59')]},
                    'link': 'http://www.junodownload.com/products/a-love-story-89-10-unmixed-tracks/1609583-02/',
                    'artists': [{'type': 'Main', 'name': 'Westbam'}], 'genre': ['Funky', 'Club House']}

        r = junodownload.Release.release_from_url(
            'http://www.junodownload.com/products/a-love-story-89-10-unmixed-tracks/1609583-02/')

        self.assertEqual(expected, r.data)

    def test_various_artists(self):
        expected = {'title': '2008 MOST USEFUL TOOLS', 'label': ['NuZone Tools'], 'released': '30 December, 2008',
                    'catalog': ['NZT 015'], 'discs': {
                1: [('1', [], 'Sygma - Nightlights', '08:42'), ('2', [], "Adolfo Morrone - I'm Nervhouse", '07:35'),
                    ('3', [], 'Jonathan Carey - The Science Of Music', '05:54'),
                    ('4', [], 'Lorenzo Venturini - New Era', '06:55'),
                    ('5', [], 'E-Mark - Anthem For Deejays Part 2', '07:00'),
                    ('6', [], 'Alex Spadoni - Sunset', '07:31'),
                    ('7', [], 'Jordan Baxxter feat Aedo - What It Feels Like For A Girl?', '07:50'),
                    ('8', [], 'Hildebrand - Raindrops', '08:39'), ('9', [], 'Dario Maffia - Phaelon', '09:05'),
                    ('10', [], 'Emerald Coast - Exhausted', '05:38'), ('11', [], 'Sygma - Children', '08:59'),
                    ('12', [], 'GoldSaint - Tonight', '06:45'), ('13', [], 'Peter Santos - Back To You', '07:34'),
                    ('14', [], 'Oscar Burnside - Dark Side', '05:34'), ('15', [], 'GoldSaint - Recharge', '08:30'),
                    ('16', [], 'Luca Lux - Wildest Dream', '07:08'), ('17', [], 'SimoX DJ - Star', '05:17'),
                    ('18', [], 'Greek S - The Sound (09 mix)', '08:37'),
                    ('19', [], 'Various - Mixed Tools 2008 (Part 1 - mixed by Sygma)', '41:34'),
                    ('20', [], 'Various - Mixed Tools 2008 (Part 2 - mixed by Peter Santos)', '38:54')]},
                    'link': 'http://www.junodownload.com/products/2008-most-useful-tools/1384246-02/',
                    'genre': ['Progressive House'], 'artists': [{'type': 'Main', 'name': 'Various'}]}

        r = junodownload.Release.release_from_url(
            'http://www.junodownload.com/products/2008-most-useful-tools/1384246-02/')

        self.assertEqual(expected, r.data)

    def test_404(self):
        r = junodownload.Release.release_from_url(
            'http://www.junodownload.com/products/2008-most-useful-tools/99999999/')
        try:
            r.data
            self.assertFalse(True)
        except junodownload.JunodownloadAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e


class ITunesTest(TestCase):
    maxDiff = None

    def test_simple_album(self):
        expected = {'title': 'Love (Remastered)', 'released': '1985', 'discs': {
            1: [('1', [], 'Nirvana', '5:26'), ('2', [], 'Big Neon Glitter', '4:51'), ('3', [], 'Love', '5:29'),
                ('4', [], 'Brother Wolf, Sister Moon', '6:47'), ('5', [], 'Rain', '3:56'), ('6', [], 'Phoenix', '5:06'),
                ('7', [], 'Hollow Man', '4:45'), ('8', [], 'Revolution', '5:26'),
                ('9', [], 'She Sells Sanctuary', '4:23'), ('10', [], 'Black Angel', '5:22')]},
                    'link': 'http://itunes.apple.com/us/album/love-remastered/id3022929?ign-mpt=uo%3D4',
                    'artists': [{'type': 'Main', 'name': 'The Cult'}],
                    'genre': ['Rock', 'Adult Alternative', 'Hard Rock', 'Alternative', 'Goth Rock', 'College Rock']}

        r = itunes.Release.release_from_url('http://itunes.apple.com/us/album/love-remastered/id3022929?ign-mpt=uo%3D4')

        self.assertEqual(expected, r.data)

    def test_multiple_cds(self):
        expected = {'title': 'Requiembryo', 'released': 'Mar 29, 2003', 'discs': {
            1: [('1', [], u'\xf7Ff\xe4hrte', '5:55'), ('2', [], 'Coming Home', '4:47'),
                ('3', [], 'De Profundis', '3:53'), ('4', [], u'Pavor Diurnus (Fremde Tr\xe4ume 1)', '1:23'),
                ('5', [], 'Duett (Das Minnellied der Incubi)', '4:37'), ('6', [], 'Schmetterflug', '2:58'),
                ('7', [], 'Frostbrand', '5:22'), ('8', [], 'Ich bin ein wahrer Satan', '5:55'),
                ('9', [], 'Erinnerungen eines Fremden', '2:16'), ('10', [], 'Raserei', '5:13'),
                ('11', [], 'Das Erwachen', '7:03'), ('12', [], 'Erinnerungen eines Fremden (Reprise)', '1:23'),
                ('13', [], 'Finger Weg! Finger!', '3:37')], 2: [('1', [], 'Requiem 01 - Introitus Interruptus', '3:21'),
                ('2', [], 'Requiem 02 - Kyrie Elesion Mercy', '3:47'),
                ('3', [], 'Requiem 03 - Kyrie Litani Agnus Die', '2:34'),
                ('4', [], 'Requiem 04 - Die arIse (Sequenz)', '5:28'),
                ('5', [], 'Requiem 05 - Nimm Mich! (Suffertorium)', '3:33'),
                ('6', [], 'Requiem 06 - Sanctus/ Benedictus', '2:38'), ('7', [], 'Requiem 07 - Lux Aeterna', '0:52'),
                ('8', [], 'Requiem 08 - Hymnus Heaven', '2:55'), ('9', [], 'Requiem 09 - Exsequien Hell', '2:42'),
                ('10', [], 'Nekrolog', '5:00'), ('11', [], u'Pavor Nocturnis (Fremde Tr\xe4ume 2)', '1:04'),
                ('12', [], 'Biotopia', '6:26'), ('13', [], 'How Far Would You Go?', '4:06'),
                ('14', [], 'Nie Mehr', '6:03'), ('15', [], u'Off\xe4hrte (Reprise)', '1:17')]},
                    'link': 'http://itunes.apple.com/us/album/requiembryo/id461460427?uo=4',
                    'artists': [{'type': 'Main', 'name': 'ASP'}],
                    'genre': ['Rock', 'Alternative', 'Goth Rock', 'Metal']}

        r = itunes.Release.release_from_url('http://itunes.apple.com/us/album/requiembryo/id461460427?uo=4')

        self.assertEqual(expected, r.data)

    def test_various_artists(self):
        expected = {'title': '2011 Warped Tour Compilation', 'released': 'Jun 07, 2011', 'discs': {
            1: [('1', [{'type': 'Main', 'name': 'Paramore'}], "For a Pessimist, I'm Pretty Optimistic", '3:48'),
                ('2', [{'type': 'Main', 'name': 'A Day to Remember'}], 'All Signs Point to Lauderdale', '3:17'),
                ('3', [{'type': 'Main', 'name': 'Set Your Goals'}], 'Certain', '3:01'),
                ('4', [{'type': 'Main', 'name': 'The Devil Wears Prada'}], 'Anatomy', '3:46'),
                ('5', [{'type': 'Main', 'name': 'Asking Alexandria'}], 'Closure', '3:58'),
                ('6', [{'type': 'Main', 'name': 'Attack Attack! (US)'}], 'A for Andrew', '3:22'),
                ('7', [{'type': 'Main', 'name': 'Big D and the Kids Table'}], 'Modern American Gypsy', '2:38'),
                ('8', [{'type': 'Main', 'name': 'Vonnegutt'}], 'Bright Eyes', '3:20'),
                ('9', [{'type': 'Main', 'name': 'Moving Mountains'}], 'Where Two Bodies Lie', '4:17'),
                ('10', [{'type': 'Main', 'name': 'The Wonder Years'}], "Don't Let Me Cave In", '3:23'),
                ('11', [{'type': 'Main', 'name': 'Neo Geo'}], "Can't Catch Me", '3:24'),
                ('12', [{'type': 'Main', 'name': 'Hellogoodbye'}], 'Finding Something to Do', '2:55'),
                ('13', [{'type': 'Main', 'name': 'Family Force 5'}], 'Wobble', '3:42'),
                ('14', [{'type': 'Main', 'name': 'Abandon All Ships'}], 'Take One Last Breath', '3:39'),
                ('15', [{'type': 'Main', 'name': 'Of Mice & Men'}], 'Purified', '3:35'),
                ('16', [{'type': 'Main', 'name': 'Veara'}], 'Pull Your Own Weight', '2:55'),
                ('17', [{'type': 'Main', 'name': 'The Dangerous Summer'}], 'Good Things', '3:38'),
                ('18', [{'type': 'Main', 'name': 'Every Avenue'}], "Tell Me I'm a Wreck", '3:39'),
                ('19', [{'type': 'Main', 'name': 'A Skylit Drive'}], 'Too Little Too Late', '3:11'),
                ('20', [{'type': 'Main', 'name': 'Big Chocolate'}], 'Sound of My Voice (feat. Weerd Science)', '3:30'),
                ('21', [{'type': 'Main', 'name': 'The Dance Party'}], "Sasha Don't Sleep", '3:27'),
                ('22', [{'type': 'Main', 'name': 'Street Dogs'}], 'Punk Rock and Roll', '2:34'),
                ('23', [{'type': 'Main', 'name': 'Blacklist Royals'}], 'Riverside', '2:55'),
                ('24', [{'type': 'Main', 'name': 'Elway'}], 'Whispers In a Shot Glass', '1:39'),
                ('25', [{'type': 'Main', 'name': 'The Copyrights'}], 'Worn Out Passport', '2:05'),
                ('26', [{'type': 'Main', 'name': 'Against Me!'}], 'Because of the Shame', '4:20'),
                ('27', [{'type': 'Main', 'name': 'Lucero'}], "I Don't Wanna Be the One", '3:09'),
                ('28', [{'type': 'Main', 'name': 'August Burns Red'}], 'Meddler', '3:53'),
                ('29', [{'type': 'Main', 'name': 'Dance Gavin Dance'}], 'Pounce Bounce', '2:26'),
                ('30', [{'type': 'Main', 'name': 'Larry and His Flask'}], 'Blood Drunk', '3:34'),
                ('31', [{'type': 'Main', 'name': 'River City Extension'}], 'Our New Intelligence', '3:54'),
                ('32', [{'type': 'Main', 'name': 'Brothers Of Brazil'}], 'Samba Around the Clock', '2:39'),
                ('33', [{'type': 'Main', 'name': 'Lionize'}], 'Your Trying to Kill Me', '2:48'),
                ('34', [{'type': 'Main', 'name': 'The Agrrolites'}], 'Complicated Girl', '2:04'),
                ('35', [{'type': 'Main', 'name': 'The Black Pacific'}], 'The System', '2:43'),
                ('36', [{'type': 'Main', 'name': 'Sharks'}], 'It All Relates', '3:10'),
                ('37', [{'type': 'Main', 'name': 'The Menzingers'}], 'Deep Sleep', '2:37'),
                ('38', [{'type': 'Main', 'name': 'Go Radio'}], 'Any Other Heart', '3:52'),
                ('39', [{'type': 'Main', 'name': 'There for Tomorrow'}], 'The Joyride', '4:09'),
                ('40', [{'type': 'Main', 'name': 'Places and Numbers'}], 'Notes from the Dead Zone', '3:05'),
                ('41', [{'type': 'Main', 'name': 'Grieves'}], 'Bloody Poetry', '3:21'),
                ('42', [{'type': 'Main', 'name': 'I Set My Friends On Fire'}], 'It Comes Naturally', '3:36'),
                ('43', [{'type': 'Main', 'name': 'Woe, Is Me'}], '[&] Delinquents', '2:55'),
                ('44', [{'type': 'Main', 'name': 'Miss May I'}], 'Relentless Chaos', '3:25'),
                ('45', [{'type': 'Main', 'name': 'Motionless In White'}], 'Creatures', '3:47'),
                ('46', [{'type': 'Main', 'name': 'The Word Alive'}], '2012', '3:01'),
                ('47', [{'type': 'Main', 'name': 'Sick of Sarah'}], 'Autograph', '3:13'),
                ('48', [{'type': 'Main', 'name': 'The Darlings'}], 'Hypnotize', '3:13'),
                ('49', [{'type': 'Main', 'name': 'To Your Demised'}], 'The Exposed', '3:29'),
                ('50', [{'type': 'Main', 'name': 'No Reservations'}], 'Continental', '3:31'),
                ('51', [{'type': 'Main', 'name': 'Winds Of Plauge'}], 'California', '3:28'),
                ('52', [{'type': 'Main', 'name': "That's Outrageous!"}], '#Winning', '2:42'),
                ('53', [{'type': 'Main', 'name': 'Eyes Set to Kill'}], 'The Secrets Between', '3:47'),
                ('54', [{'type': 'Main', 'name': 'Verah Falls'}], 'A Family Affair', '5:21'),
                ('55', [{'type': 'Main', 'name': 'The Human Abstract'}], 'Horizon to Zenith', '4:19')]},
                    'link': 'http://itunes.apple.com/us/album/2011-warped-tour-compilation/id439590029?uo=4',
                    'artists': [{'type': 'Main', 'name': 'Various'}], 'genre': ['Alternative']}

        r = itunes.Release.release_from_url(
            'http://itunes.apple.com/us/album/2011-warped-tour-compilation/id439590029?uo=4')

        self.assertEqual(expected, r.data)

    def test_non_us_store(self):
        expected = {'title': u'Puissance Ra\xef RnB 2011', 'released': '14 mars 2011', 'discs': {1: [(
        '1', [{'type': 'Main', 'name': 'DJ Idsa'}], 'Alger Casa Tunis...Ou Paris (Feat. Ap Du 113 & Reda Taliani)',
        '4:23'), ('2', [{'type': 'Main', 'name': "L'Algerino"}], 'Marseille By Night', '3:40'),
            ('3', [{'type': 'Main', 'name': 'El Matador'}], 'Allez Allez (Feat. Amar)', '3:30'),
            ('4', [{'type': 'Main', 'name': 'DJ Idsa'}], 'Bolly Rai (Feat. Tlf, Rayan & Amal)', '3:45'),
            ('5', [{'type': 'Main', 'name': 'Hasni'}], 'Rani Mourak', '3:54'),
            ('6', [{'type': 'Main', 'name': 'Zinou le Parisien'}], 'Enti Balouta', '3:48'),
            ('7', [{'type': 'Main', 'name': 'Black Barbie'}], 'Amour Kabyle (Feat. Alilou)', '3:51'),
            ('8', [{'type': 'Main', 'name': 'Cheb Sahraoui'}], 'Hasni', '3:50'),
            ('9', [{'type': 'Main', 'name': 'Marsaoui'}], 'Petitates', '3:53'),
            ('10', [{'type': 'Main', 'name': 'Rimitti'}], 'Hina Ou Hina', '3:58'),
            ('11', [{'type': 'Main', 'name': 'Rachida'}], "Ya H'Bibi", '3:48'),
            ('12', [{'type': 'Main', 'name': 'Ouarda'}], "Haya N'Aaaoulou", '3:47'),
            ('13', [{'type': 'Main', 'name': 'Chaba Djenet'}], 'Jalouse', '4:14'),
            ('14', [{'type': 'Main', 'name': 'DJ Idsa'}], 'Always On My Mind (Feat. Big Ali & Mohamed Lamine)', '3:20'),
            ('15', [{'type': 'Main', 'name': 'Chaba Kheira'}], 'Chehal Fia Houssad Yehadrou', '4:06'),
            ('16', [{'type': 'Main', 'name': 'Cheb Abbes'}], "L'Histoire Maak Bdate", '4:15'),
            ('17', [{'type': 'Main', 'name': 'Cheb Bilal'}], 'Habssine', '4:12'),
            ('18', [{'type': 'Main', 'name': 'Cheba Faiza'}], 'Mathawache Alia', '4:16'),
            ('19', [{'type': 'Main', 'name': 'Faycal'}], 'Manfoutakche Explosif Mix By Dj Meyd', '4:40'), (
            '20', [{'type': 'Main', 'name': 'DJ Idsa'}],
            'Tout Le Monde Danse (Remix) [Feat. Jesse Matador & Amal & Dollarman]', '3:40'),
            ('21', [{'type': 'Main', 'name': 'Reda Taliani'}], 'Rai Afrika (Feat. Big Ali)', '3:07'),
            ('22', [{'type': 'Main', 'name': 'Sixieme Sens'}], 'Citoyens Du Monde (Exclus) [Feat. Rahib]', '4:27'),
            ('23', [{'type': 'Main', 'name': 'Cheb Fouzi'}], 'On Va Danser (Feat. Alibi Montana)', '3:24'),
            ('24', [{'type': 'Main', 'name': 'DJ Idsa'}], 'Hit The Rai Floor (Feat. Big Ali & Cheb Akil)', '3:44'),
            ('25', [{'type': 'Main', 'name': 'Cheb Bilal'}], 'Laab Baid', '3:12'),
            ('26', [{'type': 'Main', 'name': 'Cheb Abbes'}], 'Manbghiche Alik (Feat. Mc Harage & Dj Faouzi)', '4:12'),
            ('27', [{'type': 'Main', 'name': 'Houari Manar'}], 'One Two Three Khala Galbi Yevibri', '4:05'),
            ('28', [{'type': 'Main', 'name': 'Kader Japonais'}], 'Bla Bik', '3:58'),
            ('29', [{'type': 'Main', 'name': 'Ouarda'}], 'Bouya', '3:58'),
            ('30', [{'type': 'Main', 'name': 'DJ Idsa'}], 'Chicoter (Feat. Jacky Brown & Akil)', '4:01'),
            ('31', [{'type': 'Main', 'name': 'Faycal'}], 'Mathawsich Alia By Dj Zahir', '2:23'),
            ('32', [{'type': 'Main', 'name': 'Chaba Kheira'}], 'Ya Loukane Galbak', '3:57'),
            ('33', [{'type': 'Main', 'name': 'Hasni Seghir'}], 'Gouli Wine Rak Anaya Nejika', '4:59'), (
            '34', [{'type': 'Main', 'name': 'Dj Goldfingers'}], 'La Corniche (Feat. Tunisiano & Zahouania) [Remix]',
            '4:03'),
            ('35', [{'type': 'Main', 'name': 'Elephant Man'}], 'Bullit (Feat. Mokobe Du 113 & Sheryne)', '3:21'),
            ('36', [{'type': 'Main', 'name': 'Rachida'}], 'Aar Rabi', '4:59'),
            ('37', [{'type': 'Main', 'name': 'Hasni'}], 'Ayet Manaalam', '5:13'),
            ('38', [{'type': 'Main', 'name': 'Shyneze'}], 'All Rai On Me (Feat. Mohamed Lamine)', '3:23'),
            ('39', [{'type': 'Main', 'name': 'Swen'}], 'Emmene Moi (Feat. Najim)', '3:43'),
            ('40', [{'type': 'Main', 'name': "L'Algerino"}], "M'Zia (Feat. Reda Taliani)", '3:54')], 2: [
            ('1', [{'type': 'Main', 'name': 'Algeria United'}], '1 2 3 Viva Algeria', '4:39'),
            ('2', [{'type': 'Main', 'name': 'Milano & Torino'}], 'Fort Fort', '3:24'),
            ('3', [{'type': 'Main', 'name': 'Hasni'}], 'Consulat', '3:52'),
            ('4', [{'type': 'Main', 'name': 'Reda Taliani'}], 'Ca Passe Ou Ca Casse (Feat. Tunisiano)', '3:06'),
            ('5', [{'type': 'Main', 'name': 'Cheb Sahraoui'}], 'Pas De Chance', '4:07'),
            ('6', [{'type': 'Main', 'name': 'Marsaoui'}], 'Rani Mara Hna', '4:06'),
            ('7', [{'type': 'Main', 'name': 'Kader Japonais'}], 'Adabtek Nti Bizarre', '4:03'),
            ('8', [{'type': 'Main', 'name': 'Chaba Djenet'}], 'Kedab', '4:11'),
            ('9', [{'type': 'Main', 'name': 'Chaba Kheira'}], 'Achekek Abonne Duo Avec Abbes', '3:40'),
            ('10', [{'type': 'Main', 'name': 'Cheb Abbes'}], 'Fidel (Feat. Amine Dib)', '3:50'),
            ('11', [{'type': 'Main', 'name': 'Cheb Bilal'}], 'Bafana Bafana', '4:44'),
            ('12', [{'type': 'Main', 'name': 'Ouarda'}], 'Dalmouni', '3:55'),
            ('13', [{'type': 'Main', 'name': 'Rachida'}], 'Sabat El Ouarda', '4:05'),
            ('14', [{'type': 'Main', 'name': 'Rimitti'}], 'Rah Glaibi Andak', '3:43'),
            ('15', [{'type': 'Main', 'name': 'Zinou le Parisien'}], 'Ma Nebghik', '4:31'),
            ('16', [{'type': 'Main', 'name': 'Cheba Faiza'}], 'Galbi 4 Giga', '3:59'),
            ('17', [{'type': 'Main', 'name': 'Cheba Kheira'}], 'Dayarni Fi Ainih', '3:44'),
            ('18', [{'type': 'Main', 'name': 'Faycal'}], 'Nesimik Omri Youy Youy', '3:56'),
            ('19', [{'type': 'Main', 'name': 'Hasni Seghir'}], 'Andi Madama', '3:39'),
            ('20', [{'type': 'Main', 'name': 'Houari Manar'}], 'Charikat Non Tehleb', '3:37'),
            ('21', [{'type': 'Main', 'name': 'Khaled'}], 'Aicha', '4:15'),
            ('22', [{'type': 'Main', 'name': 'Amina'}], u'Le Dernier Qui A Parl\xe9', '3:16'),
            ('23', [{'type': 'Main', 'name': 'Reda Taliani'}], 'Josephine', '4:07'),
            ('24', [{'type': 'Main', 'name': 'Onb'}], 'Bnet Paris', '4:13'),
            ('25', [{'type': 'Main', 'name': 'Ofra Haza'}], 'Im Nin Alu-2000', '3:30'),
            ('26', [{'type': 'Main', 'name': 'Chaba Kheira'}], 'Ki Yaajabni Houbi', '4:01'),
            ('27', [{'type': 'Main', 'name': 'Cheb Abbes'}], 'Mali Mali (Feat. Chabba Djenet)', '4:05'),
            ('28', [{'type': 'Main', 'name': 'Cheb Bilal'}], 'Ntiya Omri Ntiya Ma Vie Version Salsa', '4:14'),
            ('29', [{'type': 'Main', 'name': 'Faycal'}], 'Dour Dour', '4:07'),
            ('30', [{'type': 'Main', 'name': 'Houari Manar'}], 'Wajh Ghnas', '4:03'),
            ('31', [{'type': 'Main', 'name': 'Houary Dauphin'}], 'Maniche Aaref Chta Srali', '3:43'),
            ('32', [{'type': 'Main', 'name': 'Mahfoud'}], 'One Two Three (Feat. Sonia & Univers)', '3:54'),
            ('33', [{'type': 'Main', 'name': 'Kader Japonais'}], 'Shrouha Fort', '3:49'),
            ('34', [{'type': 'Main', 'name': 'Zinou le Parisien'}], 'Chira Malha', '4:00'),
            ('35', [{'type': 'Main', 'name': 'Hasni'}], 'Yaghazal', '4:02'),
            ('36', [{'type': 'Main', 'name': 'Marsaoui'}], 'Chouli', '4:03'),
            ('37', [{'type': 'Main', 'name': 'Rimitti'}], 'Liyah Liyah', '4:10'),
            ('38', [{'type': 'Main', 'name': 'Rachida'}], 'Salou Salou', '3:51'),
            ('39', [{'type': 'Main', 'name': 'Ouarda'}], 'Gendarme', '3:45'),
            ('40', [{'type': 'Main', 'name': 'Rayan'}], 'Dana Dana (Feat. Rima)', '4:04')]},
                    'link': 'http://itunes.apple.com/fr/album/puissance-rai-rnb-2011/id423552770',
                    'artists': [{'type': 'Main', 'name': 'Various'}], 'genre': ['Musiques du monde', 'Musique']}

        r = itunes.Release.release_from_url('http://itunes.apple.com/fr/album/puissance-rai-rnb-2011/id423552770')

        self.assertEqual(expected, r.data)

    def test_404(self):
        r = itunes.Release.release_from_url('http://itunes.apple.com/us/album/blubb/id999999999999')
        try:
            r.data
            self.assertFalse(True)
        except itunes.iTunesAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e

    def test_non_us_404(self):
        r = itunes.Release.release_from_url('http://itunes.apple.com/fr/album/blubb/id999999999999')
        try:
            r.data
            self.assertFalse(True)
        except itunes.iTunesAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e