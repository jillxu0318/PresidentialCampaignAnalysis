{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Prelude to campaign analysis --> in addition to analyzing how candidates present their ideas (emotion analysis) and the concepts they focus on (concept tagging), how are they running their campaigns financially?"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "collapsed": false
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/usr/local/lib/python2.7/dist-packages/ipykernel/__main__.py:20: Warning: Can't create database 'candidates'; database exists\n"
     ]
    }
   ],
   "source": [
    "import MySQLdb as mdb\n",
    "import sys\n",
    "import pandas\n",
    "import requests\n",
    "import json\n",
    "from pandas.io.json import json_normalize\n",
    "\n",
    "# Connect to the MySQL database\n",
    "con = mdb.connect(host = 'localhost', \n",
    "                  user = 'root', \n",
    "                  passwd = 'dwdstudent2015', \n",
    "                  charset='utf8', use_unicode=True);\n",
    "\n",
    "# Query to create a database\n",
    "db_name = 'candidates'\n",
    "create_db_query = \"CREATE DATABASE IF NOT EXISTS {0} DEFAULT CHARACTER SET 'utf8'\".format(db_name)\n",
    "\n",
    "# Create a database\n",
    "cursor = con.cursor()\n",
    "cursor.execute(create_db_query)\n",
    "cursor.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "collapsed": false
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/usr/local/lib/python2.7/dist-packages/ipykernel/__main__.py:16: Warning: Table 'summary' already exists\n"
     ]
    }
   ],
   "source": [
    "cursor = con.cursor()\n",
    "table_name = 'summary'\n",
    "# Create a table\n",
    "# The {0} and {1} are placeholders for the parameters in the format(....) statement\n",
    "create_table_query = '''CREATE TABLE IF NOT EXISTS {0}.{1} \n",
    "                                (cand_name varchar(250),\n",
    "                                party varchar(250),\n",
    "                                state varchar(250),\n",
    "                                next_election varchar(250),\n",
    "                                chamber varchar(250),\n",
    "                                debt varchar(250),\n",
    "                                cash_on_hand varchar(250),\n",
    "                                spent varchar(250),\n",
    "                                total varchar(250)\n",
    "                                )'''.format(db_name, table_name)\n",
    "cursor.execute(create_table_query)\n",
    "cursor.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "collapsed": false
   },
   "outputs": [],
   "source": [
    "import MySQLdb as mdb\n",
    "import sys\n",
    "import pandas\n",
    "import requests\n",
    "import json\n",
    "from pandas.io.json import json_normalize\n",
    "\n",
    "def analyzeCandidate(candidate):\n",
    "    \n",
    "    url = \"http://www.opensecrets.org/api/?method=candSummary\" + \\\n",
    "     \"&cid=\"+ candidate + \\\n",
    "     \"&cycle=2016\" + \\\n",
    "     \"&apikey=408e7bbd4e6c75a45cac1f3238254281\" + \\\n",
    "     \"&output=json\"\n",
    "    \n",
    "    resp = requests.get(url)\n",
    "    data = json.loads(resp.text)\n",
    "    \n",
    "    data = data[\"response\"][\"summary\"][\"@attributes\"]\n",
    "    \n",
    "    df = json_normalize(data)\n",
    "    \n",
    "    # We do a little bit of housecleaning and define \n",
    "    # proper data types for the data frame column\n",
    "\n",
    "    df    \n",
    "    df[\"next_election\"] = pandas.to_numeric(df[\"next_election\"])\n",
    "\n",
    "    df[\"debt\"] = pandas.to_numeric(df[\"debt\"])\n",
    "    df[\"cash_on_hand\"] = pandas.to_numeric(df[\"cash_on_hand\"])\n",
    "    df[\"spent\"] = pandas.to_numeric(df[\"spent\"])\n",
    "    df[\"total\"] = pandas.to_numeric(df[\"total\"])\n",
    "    \n",
    "    return df\n",
    "\n",
    "def deleteDatabaseTable(databaseName, tableName):\n",
    "    query_template = '''DELETE FROM {0}.{1}'''\n",
    "    cursor = con.cursor()\n",
    "    cursor.execute(query_template.format(databaseName, tableName))\n",
    "    cursor.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "def insertInDB(candidate):\n",
    "    query_template = '''INSERT INTO \n",
    "        candidates.summary(cand_name, party, state, next_election, chamber, debt, cash_on_hand, spent, total) \n",
    "        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''\n",
    "    \n",
    "    cursor = con.cursor()\n",
    "    \n",
    "    results = analyzeCandidate(candidate) \n",
    "    \n",
    "    # We iterate over the rows of the Dataframe\n",
    "    # using the iterrows() command.\n",
    "    for i, row in results.iterrows():\n",
    "        # The row variable contains the elements of a row\n",
    "        # and each field is accessible as in dictionaries\n",
    "        candidate = str(row[\"cand_name\"])\n",
    "        party = str(row[\"party\"])\n",
    "        state = str(row[\"state\"])\n",
    "        election = str(row[\"next_election\"])\n",
    "        chamber = str(row[\"chamber\"])\n",
    "        debt = str(row[\"debt\"])\n",
    "        cash = str(row[\"cash_on_hand\"])\n",
    "        spent = str(row[\"spent\"])\n",
    "        total = str(row[\"total\"])\n",
    "        query_parameters = (candidate, party, state, election, chamber, debt, cash, spent, total)\n",
    "        cursor.execute(query_template, query_parameters)\n",
    "\n",
    "    con.commit()\n",
    "    cursor.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {
    "collapsed": false
   },
   "outputs": [],
   "source": [
    "deleteDatabaseTable('candidates', 'summary')\n",
    "insertInDB('N00000528')\n",
    "insertInDB('N00023864')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {
    "collapsed": false
   },
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>candidate name</th>\n",
       "      <th>cash on hand</th>\n",
       "      <th>chamber</th>\n",
       "      <th>debt</th>\n",
       "      <th>next election</th>\n",
       "      <th>party</th>\n",
       "      <th>total spent</th>\n",
       "      <th>state</th>\n",
       "      <th>total raised</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Sanders, Bernie</td>\n",
       "      <td>17460961</td>\n",
       "      <td>Pres</td>\n",
       "      <td>0</td>\n",
       "      <td>2016</td>\n",
       "      <td>D</td>\n",
       "      <td>164667159</td>\n",
       "      <td>VT</td>\n",
       "      <td>182182143</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Trump, Donald</td>\n",
       "      <td>2111070</td>\n",
       "      <td>Pres</td>\n",
       "      <td>35926174</td>\n",
       "      <td>2016</td>\n",
       "      <td>R</td>\n",
       "      <td>46282467</td>\n",
       "      <td>NY</td>\n",
       "      <td>48393537</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "    candidate name cash on hand chamber      debt next election party  \\\n",
       "0  Sanders, Bernie     17460961    Pres         0          2016     D   \n",
       "1    Trump, Donald      2111070    Pres  35926174          2016     R   \n",
       "\n",
       "  total spent state total raised  \n",
       "0   164667159    VT    182182143  \n",
       "1    46282467    NY     48393537  "
      ]
     },
     "execution_count": 6,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import pandas as pd\n",
    "\n",
    "cur = con.cursor(mdb.cursors.DictCursor)\n",
    "cur.execute(\"SELECT * FROM candidates.summary\")\n",
    "rows = cur.fetchall()\n",
    "df = pd.DataFrame(list(rows))\n",
    "df.columns = ['candidate name', 'cash on hand', 'chamber', 'debt', 'next election', 'party', 'total spent', 'state', 'total raised']\n",
    "df"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "collapsed": true
   },
   "source": [
    "All financial numbers represent amount of money expended or raised by the Candidate's respective campaign parties (Bernie 2016 or Donald Trump for President)\n",
    "\n",
    "Candidate ID's were found by searching for the candidate name in the OpenSecrets database\n",
    "\n",
    "Sanders: https://www.opensecrets.org/pres16/candidate.php?id=N00000528\n",
    "\n",
    "Trump: https://www.opensecrets.org/pres16/candidate.php?id=N00023864"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 2",
   "language": "python",
   "name": "python2"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 2
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython2",
   "version": "2.7.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}
