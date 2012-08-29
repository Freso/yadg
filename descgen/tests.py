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

    def test_404(self):
        r = discogs.Release.release_from_url('http://www.discogs.com/Various-Gothic-File-14/release/12345')
        try:
            r.data
            self.assertFalse(True)
        except discogs.DiscogsAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e


class MusicbrainzTest(TestCase):
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
                                          {'type': 'Main', 'name': u'Ralph M\xfcller'}],
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

    def test_404(self):
        r = musicbrainz.Release.release_from_url('http://musicbrainz.org/release/12345-abcdefg')
        try:
            r.data
            self.assertFalse(True)
        except musicbrainz.MusicBrainzAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e


class BeatportTest(TestCase):
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
                    '8', [{'type': 'Main', 'name': u'Massimo Russo'}, {'type': 'Remixer', 'name': u'Italianbeat Guys'}],
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