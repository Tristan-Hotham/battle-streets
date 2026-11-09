"""The battle table: key, display name, regex on the street name, date (year, month, day), war, era, and a flag.
Only battles whose date I am sure of. Dates are the battle itself (for a siege, its end or relief, as said in the note).
flag: '' = in the clock; 'old' = before 1793, named long after the event, so outside the clock; 'amb' = the name is often
the place, a person or a colour rather than the battle, so kept out of the clock (Nile, Copenhagen, Delhi, Gibraltar, ...).
ERA: the war groups used to pool the test."""

B = [
    # key, label, regex, (y, m, d), war, flag, note
    ("armada", "Armada", r"armada", (1588, 8, 8), "Spanish Armada", "old", "Gravelines, 8 August 1588"),
    ("bannockburn", "Bannockburn", r"bannockburn", (1314, 6, 24), "Scottish independence", "old", "also a town near Stirling"),
    ("crecy", "Crecy", r"cr[eé]cy", (1346, 8, 26), "Hundred Years War", "old", ""),
    ("poitiers", "Poitiers", r"poitiers", (1356, 9, 19), "Hundred Years War", "old", ""),
    ("agincourt", "Agincourt", r"agincourt", (1415, 10, 25), "Hundred Years War", "old", ""),
    ("bosworth", "Bosworth", r"bosworth", (1485, 8, 22), "Wars of the Roses", "old", "also Market Bosworth and Husbands Bosworth"),
    ("flodden", "Flodden", r"flodden", (1513, 9, 9), "Anglo-Scottish wars", "old", ""),
    ("edgehill", "Edgehill", r"edge ?hill", (1642, 10, 23), "English Civil War", "old", "also a common hill name"),
    ("marston", "Marston Moor", r"marston moor", (1644, 7, 2), "English Civil War", "old", ""),
    ("naseby", "Naseby", r"naseby", (1645, 6, 14), "English Civil War", "old", "also the Northamptonshire village"),
    ("sedgemoor", "Sedgemoor", r"sedgemoor", (1685, 7, 6), "Monmouth Rebellion", "old", "also the Somerset district"),
    ("boyne", "Boyne", r"boyne", (1690, 7, 11), "Williamite War", "old", "Gregorian date; also the river and Scottish places"),
    ("aughrim", "Aughrim", r"aughrim", (1691, 7, 22), "Williamite War", "old", "Gregorian date"),
    ("vigo", "Vigo", r"vigo", (1702, 10, 23), "Spanish Succession", "amb", "also the Spanish port"),
    ("blenheim", "Blenheim", r"blenheim", (1704, 8, 13), "Spanish Succession", "old", "often via Blenheim Palace"),
    ("gibraltar", "Gibraltar", r"gibraltar", (1704, 8, 4), "Spanish Succession", "amb", "usually the Rock, not its capture"),
    ("ramillies", "Ramillies", r"ramillies", (1706, 5, 23), "Spanish Succession", "old", ""),
    ("almanza", "Almanza", r"almanza", (1707, 4, 25), "Spanish Succession", "old", ""),
    ("oudenarde", "Oudenarde", r"oudenarde", (1708, 7, 11), "Spanish Succession", "old", ""),
    ("malplaquet", "Malplaquet", r"malplaquet", (1709, 9, 11), "Spanish Succession", "old", ""),
    ("portobello", "Portobello", r"porto ?bello", (1739, 11, 22), "Jenkins' Ear", "amb", "often via Portobello places (Edinburgh, London farm)"),
    ("dettingen", "Dettingen", r"dettingen", (1743, 6, 27), "Austrian Succession", "old", ""),
    ("fontenoy", "Fontenoy", r"fontenoy", (1745, 5, 11), "Austrian Succession", "old", ""),
    ("culloden", "Culloden", r"culloden", (1746, 4, 16), "Jacobite rising", "old", "also the village by Inverness"),
    ("minorca", "Minorca", r"minorca", (1756, 5, 20), "Seven Years War", "amb", "usually the island"),
    ("plassey", "Plassey", r"plassey", (1757, 6, 23), "Seven Years War", "old", ""),
    ("louisburg", "Louisburg", r"louisbo?urg", (1758, 7, 26), "Seven Years War", "old", ""),
    ("minden", "Minden", r"minden", (1759, 8, 1), "Seven Years War", "old", ""),
    ("quebec", "Quebec", r"quebec", (1759, 9, 13), "Seven Years War", "amb", "usually the city or province"),
    ("quiberon", "Quiberon", r"quiberon", (1759, 11, 20), "Seven Years War", "old", ""),
    ("belleisle", "Belle Isle", r"belle ?isle", (1761, 6, 7), "Seven Years War", "old", "capture of Belle Ile"),
    ("havannah", "Havannah", r"havannah?", (1762, 8, 13), "Seven Years War", "old", "capture of Havana"),
    # the clock: 1793 onwards
    ("stvincent", "St Vincent", r"(st\.?|saint) vincent", (1797, 2, 14), "French Revolutionary Wars", "amb", "usually the saint or Earl St Vincent"),
    ("camperdown", "Camperdown", r"camperdown", (1797, 10, 11), "French Revolutionary Wars", "", ""),
    ("nile", "Nile", r"nile", (1798, 8, 1), "French Revolutionary Wars", "amb", "usually the river"),
    ("aboukir", "Aboukir", r"aboukir", (1798, 8, 1), "French Revolutionary Wars", "amb", "the Nile (1798) or the landing (1801)"),
    ("seringapatam", "Seringapatam", r"seringapatam", (1799, 5, 4), "Fourth Anglo-Mysore War", "", ""),
    ("copenhagen", "Copenhagen", r"copenhagen", (1801, 4, 2), "French Revolutionary Wars", "amb", "London's Copenhagen Street is from Copenhagen House"),
    ("alexandria", "Alexandria", r"alexandria", (1801, 3, 21), "French Revolutionary Wars", "amb", "usually the city (or 1882)"),
    ("assaye", "Assaye", r"assaye", (1803, 9, 23), "Second Anglo-Maratha War", "", ""),
    ("trafalgar", "Trafalgar", r"trafalgar", (1805, 10, 21), "Napoleonic Wars", "", ""),
    ("maida", "Maida", r"maida", (1806, 7, 4), "Napoleonic Wars", "", "Maida Vale is named after it, through an inn"),
    ("vimeiro", "Vimeiro", r"vimiera|vimeiro", (1808, 8, 21), "Peninsular War", "", ""),
    ("corunna", "Corunna", r"corunna", (1809, 1, 16), "Peninsular War", "", ""),
    ("talavera", "Talavera", r"talavera", (1809, 7, 28), "Peninsular War", "", ""),
    ("busaco", "Busaco", r"busaco", (1810, 9, 27), "Peninsular War", "", ""),
    ("albuera", "Albuera", r"albuera", (1811, 5, 16), "Peninsular War", "", ""),
    ("badajoz", "Badajoz", r"badajoz", (1812, 4, 6), "Peninsular War", "", "storming of the fortress"),
    ("salamanca", "Salamanca", r"salamanca", (1812, 7, 22), "Peninsular War", "", ""),
    ("vittoria", "Vittoria", r"vitt?oria", (1813, 6, 21), "Peninsular War", "", ""),
    ("waterloo", "Waterloo", r"waterloo", (1815, 6, 18), "Napoleonic Wars", "", ""),
    ("algiers", "Algiers", r"algiers", (1816, 8, 27), "Bombardment of Algiers", "", ""),
    ("navarino", "Navarino", r"navarino", (1827, 10, 20), "Greek War of Independence", "", ""),
    ("cabul", "Cabul", r"cabul|kabul", (1842, 9, 15), "First Anglo-Afghan War", "amb", "usually the city; dates differ"),
    ("meeanee", "Meeanee", r"meeanee", (1843, 2, 17), "Conquest of Sind", "", ""),
    ("scinde", "Scinde", r"scinde", (1843, 2, 17), "Conquest of Sind", "amb", "the province"),
    ("moodkee", "Moodkee", r"moodkee", (1845, 12, 18), "First Anglo-Sikh War", "", ""),
    ("ferozeshah", "Ferozeshah", r"ferozeshah", (1845, 12, 21), "First Anglo-Sikh War", "", ""),
    ("aliwal", "Aliwal", r"aliwal", (1846, 1, 28), "First Anglo-Sikh War", "", ""),
    ("sobraon", "Sobraon", r"sobraon", (1846, 2, 10), "First Anglo-Sikh War", "", ""),
    ("goojerat", "Goojerat", r"goojerat", (1849, 2, 21), "Second Anglo-Sikh War", "", ""),
    ("alma", "Alma", r"alma", (1854, 9, 20), "Crimean War", "", ""),
    ("balaclava", "Balaclava", r"balaclava|balaklava", (1854, 10, 25), "Crimean War", "", ""),
    ("inkerman", "Inkerman", r"inkerm[ae]n", (1854, 11, 5), "Crimean War", "", ""),
    ("sebastopol", "Sebastopol", r"sebastopol|sevastopol", (1855, 9, 9), "Crimean War", "", "fall of the city after the siege"),
    ("crimea", "Crimea", r"crimea", (1855, 9, 9), "Crimean War", "amb", "the peninsula"),
    ("delhi", "Delhi", r"delhi", (1857, 9, 20), "Indian Rebellion", "amb", "usually the city"),
    ("cawnpore", "Cawnpore", r"cawnpore", (1857, 7, 16), "Indian Rebellion", "", ""),
    ("lucknow", "Lucknow", r"lucknow", (1857, 11, 16), "Indian Rebellion", "", "second relief"),
    ("magenta", "Magenta", r"magenta", (1859, 6, 4), "Second Italian War", "amb", "usually the colour, itself named after the battle"),
    ("solferino", "Solferino", r"solferino", (1859, 6, 24), "Second Italian War", "", ""),
    ("ulundi", "Ulundi", r"ulundi", (1879, 7, 4), "Anglo-Zulu War", "", ""),
    ("kandahar", "Kandahar", r"kandahar|candahar", (1880, 9, 1), "Second Anglo-Afghan War", "amb", "the city; Roberts's march was 1880"),
    ("majuba", "Majuba", r"majuba", (1881, 2, 27), "First Boer War", "", ""),
    ("telelkebir", "Tel el Kebir", r"tel[- ]el[- ]kebir", (1882, 9, 13), "Anglo-Egyptian War", "", ""),
    ("khartoum", "Khartoum", r"khartoum", (1885, 1, 26), "Mahdist War", "", "fall of Khartoum and death of Gordon"),
    ("chitral", "Chitral", r"chitral", (1895, 4, 20), "Chitral Expedition", "", "relief of Chitral"),
    ("dargai", "Dargai", r"dargai", (1897, 10, 20), "Tirah Campaign", "", ""),
    ("tirah", "Tirah", r"tirah", (1897, 10, 20), "Tirah Campaign", "", ""),
    ("omdurman", "Omdurman", r"omdurman", (1898, 9, 2), "Mahdist War", "", ""),
    ("modder", "Modder River", r"modder", (1899, 11, 28), "Second Boer War", "", ""),
    ("colenso", "Colenso", r"colenso", (1899, 12, 15), "Second Boer War", "", ""),
    ("spionkop", "Spion Kop", r"spion ?kop", (1900, 1, 24), "Second Boer War", "", "also football terraces named after it"),
    ("kimberley", "Kimberley", r"kimberley", (1900, 2, 15), "Second Boer War", "amb", "often the Earl of Kimberley or Kimberley, Notts"),
    ("paardeberg", "Paardeberg", r"paardeberg", (1900, 2, 27), "Second Boer War", "", ""),
    ("tugela", "Tugela", r"tugela", (1900, 2, 27), "Second Boer War", "", "Tugela Heights"),
    ("ladysmith", "Ladysmith", r"ladysmith", (1900, 2, 28), "Second Boer War", "", "relief of Ladysmith"),
    ("mafeking", "Mafeking", r"mafeking", (1900, 5, 17), "Second Boer War", "", "relief of Mafeking"),
    ("mons", "Mons", r"mons", (1914, 8, 23), "First World War", "", ""),
    ("marne", "Marne", r"marne", (1914, 9, 6), "First World War", "", ""),
    ("ypres", "Ypres", r"ypres", (1914, 10, 19), "First World War", "", "first battle"),
    ("gallipoli", "Gallipoli", r"gallipoli", (1915, 4, 25), "First World War", "", ""),
    ("anzac", "Anzac", r"anzac", (1915, 4, 25), "First World War", "", ""),
    ("verdun", "Verdun", r"verdun", (1916, 2, 21), "First World War", "", ""),
    ("jutland", "Jutland", r"jutland", (1916, 5, 31), "First World War", "", ""),
    ("somme", "Somme", r"somme", (1916, 7, 1), "First World War", "", ""),
    ("arras", "Arras", r"arras", (1917, 4, 9), "First World War", "", ""),
    ("vimy", "Vimy", r"vimy", (1917, 4, 9), "First World War", "", ""),
    ("messines", "Messines", r"messines", (1917, 6, 7), "First World War", "", ""),
    ("cambrai", "Cambrai", r"cambrai", (1917, 11, 20), "First World War", "", ""),
    ("zeebrugge", "Zeebrugge", r"zeebrugge", (1918, 4, 23), "First World War", "", ""),
    ("dunkirk", "Dunkirk", r"dunkirk", (1940, 5, 26), "Second World War", "amb", "an old English place name too (Dunkirk in Kent, Nottingham, Cheshire), long before 1940"),
    ("tobruk", "Tobruk", r"tobruk", (1941, 4, 10), "Second World War", "", "siege"),
    ("alamein", "Alamein", r"alamein", (1942, 10, 23), "Second World War", "", "second battle"),
    ("stalingrad", "Stalingrad", r"stalingrad", (1942, 8, 23), "Second World War", "", ""),
    ("anzio", "Anzio", r"anzio", (1944, 1, 22), "Second World War", "", ""),
    ("cassino", "Cassino", r"cassino", (1944, 1, 17), "Second World War", "", ""),
    ("kohima", "Kohima", r"kohima", (1944, 4, 4), "Second World War", "", ""),
    ("imphal", "Imphal", r"imphal", (1944, 3, 8), "Second World War", "", ""),
    ("arnhem", "Arnhem", r"arnhem", (1944, 9, 17), "Second World War", "", ""),
    ("falklands", "Falklands", r"falklands?", (1982, 4, 2), "Falklands War", "amb", "the islands"),
]


def era(y):
    if y < 1793: return "before 1793"
    if y <= 1815: return "Napoleonic 1793 to 1815"
    if y < 1854: return "1816 to 1853"
    if y <= 1856: return "Crimea 1854 to 1856"
    if y <= 1858: return "Indian Rebellion 1857"
    if y < 1899: return "1859 to 1898"
    if y <= 1902: return "Boer War 1899 to 1902"
    if y <= 1918: return "First World War"
    if y <= 1945: return "Second World War"
    return "after 1945"


ERAS = ["before 1793", "Napoleonic 1793 to 1815", "1816 to 1853", "Crimea 1854 to 1856", "Indian Rebellion 1857", "1859 to 1898",
        "Boer War 1899 to 1902", "First World War", "Second World War", "after 1945"]
BKEY = {b[0]: b for b in B}
