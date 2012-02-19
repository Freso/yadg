from django import template

register = template.Library()

@register.simple_tag
def wrapartists(artists, artist_format_string, separator, last_separator):
    output = u''
    artist_count = len(artists)
    
    i = 0
    
    for artist in artists:
        output += artist_format_string % artist
        
        if i < artist_count - 2:
            output += separator
        elif i < artist_count - 1:
            output += last_separator
        
        i += 1
    
    return output