import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db.models import Sum

POSITON = (
        (1, "Picther"),
        (2, "Catcher"),
        (3, "First baseman"),
        (4, "Second baseman"),
        (5, "Third baseman"),
        (6, "Shortstop"),
        (7, "Outfielder"),
        (0, "Desinated Hitter"),
        (-1, "Not position")
    )

INGAME_POSITON = (
        (1, "Picther"),
        (2, "Catcher"),
        (3, "First baseman"),
        (4, "Second baseman"),
        (5, "Third baseman"),
        (6, "Shortstop"),
        (7, "Left fielder"),
        (8, "Center fielder"),
        (9, "Right fielder"),
        (0, "Desinated Hitter"),
        (-1, "Not position")
)

HAND = (
    ('S', "Switch"),
    ('L', "Left"),
    ('R', "Right"),
)

STATUS = (
    (-1, "Upcoming"),
    (0, "In progress"),
    (1, "Completed"),
)

PLAYER_STATUS = (
    (-1, "Quited"),
    (0, "Inactive"),
    (1, "Active"),
)

EMAIL_SEND = (
    (-1, "False"),
    (0, "Pending"),
    (1, "True"),
)

TRANSACTION_TYPE = (
    (1, "Present"),
    (2, "League prize"),
    (3, "Monthly fund"),
    (4, "Other add"),
    (-1, "Buy item"),
    (-2, "Held event"),
    (-3, "Give present"),
    (-4, "Other minus"),
)

EQUIPMENT_TYPE = (
    (0, "Other"),
    (1, "Bat"),
    (2, "Ball"),
    (3, "Glove"),
)

OUTCOME_TYPE = (
    (1, "Strikeout Looking"),
    (2, "Strikeout Swinging"),
    (3, "Groundout"),
    (4, "Pop/Flyout"),
    (5, "Sacrifice Fly"),
    (6, "Sacrifice Bunt"),
    (7, "Infield Fly"),
    (8, "Dropped 3rd strike"),
    (9, "Ground into Double Play"),
    (10, "Ground into Triple Play"),
    (11, "Walk"),
    (12, "Intentional Walk"),
    (13, "Single"),
    (14, "Double"),
    (15, "Triple"),
    (16, "Homerun"),
    (17, "Inside park Homerun"),
    (18, "Error"),
    (19, "Hit by pitch"),
    (20, "Fielder choice"),
    (21, "Catcher interference"),
    (22, "Fly into Double Play"),
    (23, "Fly into Triple Play"),
    (24, "Stolen base"),
)

class Team(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    shortName = models.CharField(max_length=4, unique=True, db_index=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    homeStadium = models.CharField(max_length=500, blank=True, null=True)
    foundedDate = models.DateField(null=True, blank=True)
    logo = models.ImageField(
        upload_to="logos/", default="logos/logo.png", null=True, blank=True)
    logo_str = models.TextField(blank=True, null=True)
    teamFund = models.BigIntegerField(default=0, blank=True)


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(
        help_text="Date of birth", blank=True, null=True)
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/avatar.png", blank=True, null=True)
    avatar_str = models.TextField(blank=True, null=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, blank=True, null=True)
    firstName = models.CharField(max_length=30, blank=True)
    lastName = models.CharField(max_length=30, blank=True)
    homeTown = models.TextField(null=True, blank=True)
    jerseyNumber = models.IntegerField(null=True, blank=True, default=-1)
    phoneNumber = models.CharField(max_length=11, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)

class JoinRequest(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    accepted = models.IntegerField(
        choices=EMAIL_SEND,
        max_length=1,
        blank=True,
        default=-1
    )
    created_at = models.DateTimeField(blank=True, null=True)

class Player(models.Model):
    firstName = models.CharField(max_length=30, blank=True)
    lastName = models.CharField(max_length=30, blank=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, blank=True, null=True)
    firstPos = models.IntegerField(
        choices=POSITON,
        blank=True,
        null=True,
        default=-1,
    )
    secondPos = models.IntegerField(
        choices=POSITON,
        blank=True,
        null=True,
        default=-1,
    )
    weight = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    birthDate = models.DateField(null=True, blank=True)
    homeTown = models.TextField(null=True, blank=True)
    jerseyNumber = models.IntegerField(null=True, blank=True, default=-1)
    phoneNumber = models.CharField(max_length=11, null=True, blank=True)
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/avatar.png", blank=True, null=True)
    avatar_str = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True) # Player email is nesscessary for manager to send important information
    batHand = models.CharField(
        choices=HAND,
        max_length=1,
        blank=True,
        null=True
    )
    throwHand = models.CharField(
        choices=HAND,
        max_length=1,
        blank=True,
        null=True
    )
    status = models.IntegerField(
        choices=PLAYER_STATUS,
        default=1,
        null=True,
        blank=True
    )

    @property
    def games(self):
        return PlayerGame.objects.filter(player=self)

    @property
    def plateApperance(self):
        batter_games = self.games
        if batter_games:
            plateApperances = sum(batter_game.plateApperance for batter_game in batter_games)
            return plateApperances
        return 0
    
    @property
    def runBattedIn(self):
        batter_games = self.games
        if batter_games:
            runBattedIns = sum(batter_game.runBattedIn for batter_game in batter_games)
            return runBattedIns
        return 0
    
    @property
    def single(self):
        batter_games = self.games
        if batter_games:
            singles = sum(batter_game.single for batter_game in batter_games)
            return singles
        return 0
    
    @property
    def double(self):
        batter_games = self.games
        if batter_games:
            doubles = sum(batter_game.double for batter_game in batter_games)
            return doubles
        return 0
    
    @property
    def triple(self):
        batter_games = self.games
        if batter_games:
            triples = sum(batter_game.triple for batter_game in batter_games)
            return triples
        return 0
    
    @property
    def homeRun(self):
        batter_games = self.games
        if batter_games:
            homeRuns = sum(batter_game.homeRun for batter_game in batter_games)
            return homeRuns
        return 0
    
    @property
    def baseOnBall(self):
        batter_games = self.games
        if batter_games:
            baseOnBalls = sum(batter_game.baseOnBall for batter_game in batter_games)
            return baseOnBalls
        return 0
    
    @property
    def intentionalBB(self):
        batter_games = self.games
        if batter_games:
            intentionalBBs = sum(batter_game.intentionalBB for batter_game in batter_games)
            return intentionalBBs
        return 0

    @property
    def hitByPitch(self):
        batter_games = self.games
        if batter_games:
            hitByPitchs = sum(batter_game.hitByPitch for batter_game in batter_games)
            return hitByPitchs
        return 0
    @property
    def strikeOut(self):
        batter_games = self.games
        if batter_games:
            strikeOuts = sum(batter_game.strikeOut for batter_game in batter_games)
            return strikeOuts
        return 0
    
    @property
    def fielderChoice(self):
        batter_games = self.games
        if batter_games:
            fielderChoices = sum(batter_game.fielderChoice for batter_game in batter_games)
            return fielderChoices
        return 0
    
    @property
    def sacrificeFly(self):
        batter_games = self.games
        if batter_games:
            sacrificeFlys = sum(batter_game.sacrificeFly for batter_game in batter_games)
            return sacrificeFlys
        return 0
    
    @property
    def sacrificeBunt(self):
        batter_games = self.games
        if batter_games:
            sacrificeBunts = sum(batter_game.sacrificeBunt for batter_game in batter_games)
            return sacrificeBunts
        return 0
    
    @property
    def stolenBase(self):
        batter_games = self.games
        if batter_games:
            stolenBases = sum(batter_game.stolenBase for batter_game in batter_games)
            return stolenBases
        return 0
    
    @property
    def leftOnBase(self):
        batter_games = self.games
        if batter_games:
            leftOnBases = sum(batter_game.leftOnBase for batter_game in batter_games)
            return leftOnBases
        return 0
    
    @property
    def doublePlay(self):
        batter_games = self.games
        if batter_games:
            doublePlays = sum(batter_game.doublePlay for batter_game in batter_games)
            return doublePlays
        return 0
    
    @property
    def triplePlay(self):
        batter_games = self.games
        if batter_games:
            triplePlays = sum(batter_game.triplePlay for batter_game in batter_games)
            return triplePlays
        return 0
    
    @property
    def run(self):
        batter_games = self.games
        if batter_games:
            runs = sum(batter_game.run for batter_game in batter_games)
            return runs
        return 0
    
    @property
    def onBaseByError(self):
        batter_games = self.games
        if batter_games:
            onBaseByErrors = sum(batter_game.onBaseByError for batter_game in batter_games)
            return onBaseByErrors
        return 0
    
    @property
    def putOut(self):
        batter_games = self.games
        if batter_games:
            putOuts = sum(batter_game.putOut for batter_game in batter_games)
            return putOuts
        return 0
    
    @property
    def assist(self):
        batter_games = self.games
        if batter_games:
            assists = sum(batter_game.assist for batter_game in batter_games)
            return assists
        return 0
    
    @property
    def error(self):
        batter_games = self.games
        if batter_games:
            errors = sum(batter_game.error for batter_game in batter_games)
            return errors
        return 0
    
    @property
    def totalInGameOut(self):
        batter_games = self.games
        if batter_games:
            totalInGameOuts = sum(batter_game.totalInGameOut for batter_game in batter_games)
            return totalInGameOuts
        return 0
    
    @property
    def totalBatterFaced(self):
        batter_games = self.games
        if batter_games:
            totalBatterFaceds = sum(batter_game.totalBatterFaced for batter_game in batter_games)
            return totalBatterFaceds
        return 0
    
    @property
    def oppHit(self):
        batter_games = self.games
        if batter_games:
            oppHits = sum(batter_game.oppHit for batter_game in batter_games)
            return oppHits
        return 0
    
    @property
    def oppRun(self):
        batter_games = self.games
        if batter_games:
            oppRuns = sum(batter_game.oppRun for batter_game in batter_games)
            return oppRuns
        return 0
    
    @property
    def earnedRun(self):
        batter_games = self.games
        if batter_games:
            earnedRuns = sum(batter_game.earnedRun for batter_game in batter_games)
            return earnedRuns
        return 0
    
    @property
    def oppBaseOnBall(self):
        batter_games = self.games
        if batter_games:
            oppBaseOnBalls = sum(batter_game.oppBaseOnBall for batter_game in batter_games)
            return oppBaseOnBalls
        return 0
    
    @property
    def oppStrikeOut(self):
        batter_games = self.games
        if batter_games:
            oppStrikeOuts = sum(batter_game.oppStrikeOut for batter_game in batter_games)
            return oppStrikeOuts
        return 0
    
    @property
    def hitBatter(self):
        batter_games = self.games
        if batter_games:
            hitBatters = sum(batter_game.hitBatter for batter_game in batter_games)
            return hitBatters
        return 0
    
    @property
    def balk(self):
        batter_games = self.games
        if batter_games:
            balks = sum(batter_game.balk for batter_game in batter_games)
            return balks
        return 0
    
    @property
    def wildPitch(self):
        batter_games = self.games
        if batter_games:
            wildPitchs = sum(batter_game.wildPitch for batter_game in batter_games)
            return wildPitchs
        return 0
    
    @property
    def oppHomeRun(self):
        batter_games = self.games
        if batter_games:
            oppHomeRuns = sum(batter_game.oppHomeRun for batter_game in batter_games)
            return oppHomeRuns
        return 0
    
    @property
    def firstPitchStrike(self):
        batter_games = self.games
        if batter_games:
            firstPitchStrikes = sum(batter_game.firstPitchStrike for batter_game in batter_games)
            return firstPitchStrikes
        return 0
    
    @property
    def pickOff(self):
        batter_games = self.games
        if batter_games:
            pickOffs = sum(batter_game.pickOff for batter_game in batter_games)
            return pickOffs
        return 0
    
    @property
    def atBat(self):
        return self.plateApperance - self.baseOnBall - self.hitByPitch - self.sacrificeFly - self.sacrificeBunt

    @property
    def hit(self):
        return self.single + self.double + self.triple + self.homeRun
    
    @property
    def battingAverage(self):
        if self.atBat == 0:
            return "-"
        return "{:.3f}".format(self.hit/self.atBat)
    
    @property
    def onBasePercentage(self):
        up = self.hit + self.baseOnBall + self.hitByPitch
        down = self.atBat + self.baseOnBall + self.hitByPitch + self.sacrificeFly
        if down == 0:
            return "-"
        return "{:.3f}".format(up/down)

    @property
    def sluggingPercentage(self):
        up = self.single + self.double*2 + self.triple*3 + self.homeRun*4
        down = self.atBat
        if down == 0:
            return "-"
        return "{:.3f}".format(up/down)

    @property
    def onBasePlusSlugging(self):
        if self.onBasePercentage == '-' and self.sluggingPercentage == '-':
            return '-'
        elif self.onBasePercentage == '-':
            return self.sluggingPercentage
        elif self.sluggingPercentage == '-':
            return self.onBasePercentage
        else:
            return "{:.3f}".format(float(self.sluggingPercentage) + float(self.onBasePercentage))
    
    @property
    def weightedOnBasePercentage(self):
        up = self.baseOnBall*0.69 + self.hitByPitch*0.72 + self.single*0.89 + self.double*1.27 + self.triple*1.62 + self.homeRun*2.1 
        down = self.atBat + self.baseOnBall + self.sacrificeFly + self.hitByPitch

        if down == 0:
            return '-'
        return "{:.3f}".format(up/down)
    
    @property
    def totalChance(self):
        return self.putOut + self.assist + self.error
    
    @property
    def fieldingPercentage(self):
        if self.totalChance == 0:
            return '-'
        up = self.putOut + self.assist
        return "{:.3f}".format(up/self.totalChance)
    
    @property
    def earnedRunAverage(self):
        batter_games = self.games
        if (batter_games):
            up = sum(batter_game.earnedRun*batter_game.game.inningERA*3 for batter_game in batter_games)
            down = self.totalInGameOut
            if down == 0:
                if self.earnedRun != 0:
                    return 'INF'
                else:
                    return '-'
            return "{:.2f}".format(up/down)
        else:
            return '-'
        
    @property
    def walkAndHitPerInning(self):
        up = self.oppBaseOnBall + self.oppHit
        down = (self.totalInGameOut // 3) + ((self.totalInGameOut % 3) / 3)
        if self.totalInGameOut == 0:
            if up != 0:
                return 'INF'
            else:
                return '-'
        return "{:.1f}".format(up/down)
    
    @property
    def runnerAllowed(self):
        return self.oppHit + self.oppBaseOnBall + self.hitBatter
    

    @property
    def firstPitchStrikePercentage(self):
        if self.totalBatterFaced == 0:
            return '-'
        return "{:.3f}".format(self.firstPitchStrike/self.totalBatterFaced)
    
    @property
    def fieldingIndependentPitching(self):
        if self.totalInGameOut == 0:
            return '-'
        return ((self.oppHomeRun*13 + (self.hitBatter + self.oppBaseOnBall)*3 - self.oppStrikeOut*2) / ((self.totalInGameOut // 3) + ((self.totalInGameOut % 3) / 3))) + 3.2
    
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, blank=True, null=True)
    location = models.TextField(max_length=500, blank=True, null=True)
    timeStart = models.DateTimeField(default=datetime.datetime.now())
    timeEnd = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(
        choices= STATUS,
        blank=True,
        default=-1
    )

class Practice(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, blank=True, null=True)
    location = models.TextField(max_length=500, blank=True, null=True)
    timeStart = models.DateTimeField(default=datetime.datetime.now())
    timeEnd = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(
        choices= STATUS,
        blank=True,
        default=-1
    )


class PlayerEvent(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ATTEND_STATUS = (
        (1, "Attend"),
        (0, "Not attend"),
        (2, "Pending")
    )
    status = models.IntegerField(
        choices=ATTEND_STATUS,
        blank=True,
        default=2,
    )

class ManagerEvent(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ATTEND_STATUS = (
        (1, "Attend"),
        (0, "Not attend"),
        (2, "Pending")
    )
    status = models.IntegerField(
        choices=ATTEND_STATUS,
        blank=True,
        default=2,
    )

class PlayerPractice(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    ATTEND_STATUS = (
        (1, "Attend"),
        (0, "Not attend"),
        (2, "Pending")
    )
    status = models.IntegerField(
        choices=ATTEND_STATUS,
        blank=True,
        default=2,
    )

class League(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    timeStart = models.DateField(blank=True, null=True)
    timeEnd = models.DateField(blank=True, null=True)
    ACHIEVE_STATUS = (
        (1, "Champion"),
        (2, "Runner-up"),
        (3, "Third place"),
        (0, "No achivement")
    )
    achieve = models.IntegerField(
        choices=ACHIEVE_STATUS,
        blank=True,
        default=0,
    )
    status = models.IntegerField(
        choices= STATUS,
        blank=True,
        default=-1
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, blank=True, null=True)

class Game(models.Model):
    oppTeam = models.CharField(max_length=200)
    oppTeamShort = models.CharField(max_length=4)
    league = models.ForeignKey(League, blank=True, null=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    timeStart = models.DateTimeField(default=datetime.datetime.now())
    timeEnd = models.DateTimeField(blank=True, null=True)
    stadium = models.CharField(max_length=500, blank=True, null=True)
    inningERA = models.IntegerField(blank=True, null=True, default=7)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(
        choices= STATUS,
        blank=True,
        default=-1
    )
    # team_score = models.IntegerField(blank=True, null=True, default=0)
    # team_hit = models.IntegerField(blank=True, null=True, default=0)
    # team_err = models.IntegerField(blank=True, null=True, default=0)
    # opp_score = models.IntegerField(blank=True, null=True, default=0)
    # opp_hit = models.IntegerField(blank=True, null=True, default=0)
    # opp_err = models.IntegerField(blank=True, null=True, default=0)

    @property
    def team_score(self):
        batter_games = PlayerGame.objects.filter(game=self)
        if batter_games:
            team_scores = sum(batter_game.run for batter_game in batter_games)
            return team_scores
        return 0
    
    @property
    def team_error(self):
        fielder_games = PlayerGame.objects.filter(game=self)
        if fielder_games:
            team_error = sum(fielder_game.error for fielder_game in fielder_games)
            return team_error
        return 0
    
    @property
    def team_hit(self):
        batter_games = PlayerGame.objects.filter(game=self)
        if batter_games:
            team_hits = sum(batter_game.hit for batter_game in batter_games)
            return team_hits
        return 0
    
    @property
    def team_inning_score(self):
        at_bats = list(AtBat.objects.filter(game=self))
        max_inning = at_bats[-1].inning if at_bats else 0
        arr = []
        if at_bats:
            for i in range(1, max_inning+1):
                inning_at_bats = [ab for ab in at_bats if ab.isOffense == 1 and ab.inning == i]
                inning_scores = [ab.teamScore for ab in inning_at_bats] if inning_at_bats else None
                inning_score = max(inning_scores) if inning_scores else None
                arr.append(inning_score)
        return arr
    
    @property
    def opp_score(self):
        pitcher_games = PlayerGame.objects.filter(game=self)
        if pitcher_games:
            opp_scores = sum(pitcher_game.oppRun for pitcher_game in pitcher_games)
            return opp_scores
        return 0
    
    @property
    def opp_error(self):
        batter_games = PlayerGame.objects.filter(game=self)
        if batter_games:
            opp_error = sum(batter_game.onBaseByError for batter_game in batter_games)
            return opp_error
        return 0
    
    @property
    def opp_hit(self):
        pitcher_games = PlayerGame.objects.filter(game=self)
        if pitcher_games:
            opp_hits = sum(pitcher_game.oppHit for pitcher_game in pitcher_games)
            return opp_hits
        return 0
    
    @property
    def opp_inning_score(self):
        at_bats = list(AtBat.objects.filter(game=self))
        max_inning = at_bats[-1].inning if at_bats else 0
        arr = []
        if at_bats:
            for i in range(1, max_inning+1):
                inning_at_bats = [ab for ab in at_bats if ab.isOffense == 0 and ab.inning == i]
                inning_scores = [ab.oppScore for ab in inning_at_bats] if inning_at_bats else None
                inning_score = max(inning_scores) if inning_scores else None
                arr.append(inning_score)
        return arr

class PlayerGame(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    position = models.IntegerField(default=0, null=True, blank=True)
    plateApperance = models.IntegerField(default=0, null=True, blank=True)
    battingOrder = models.IntegerField(default=0, null=True, blank=True)
    # atBat = models.IntegerField(default=0, null=True, blank=True)
    runBattedIn = models.IntegerField(default=0, null=True, blank=True)
    # hit = models.IntegerField(default=0, null=True, blank=True)
    single = models.IntegerField(default=0, null=True, blank=True)
    double = models.IntegerField(default=0, null=True, blank=True)
    triple = models.IntegerField(default=0, null=True, blank=True)
    homeRun = models.IntegerField(default=0, null=True, blank=True)
    baseOnBall = models.IntegerField(default=0, null=True, blank=True)
    intentionalBB = models.IntegerField(default=0, null=True, blank=True)
    hitByPitch =  models.IntegerField(default=0, null=True, blank=True)
    strikeOut = models.IntegerField(default=0, null=True, blank=True)
    fielderChoice = models.IntegerField(default=0, null=True, blank=True)
    sacrificeFly = models.IntegerField(default=0, null=True, blank=True)
    sacrificeBunt = models.IntegerField(default=0, null=True, blank=True)
    stolenBase = models.IntegerField(default=0, null=True, blank=True)
    leftOnBase = models.IntegerField(default=0, null=True, blank=True)
    doublePlay = models.IntegerField(default=0, null=True, blank=True)
    triplePlay = models.IntegerField(default=0, null=True, blank=True)
    run = models.IntegerField(default=0, null=True, blank=True)
    onBaseByError = models.IntegerField(default=0, null=True, blank=True)
    position = models.IntegerField(
        choices=INGAME_POSITON,
        blank=True,
        default=-1,
    )
    playedPos = ArrayField(models.IntegerField(
        choices=INGAME_POSITON,
        blank=True,
        default=-1,
    ))
    # totalChance = models.IntegerField(default=0)
    putOut = models.IntegerField(default=0, null=True, blank=True)
    assist = models.IntegerField(default=0, null=True, blank=True)
    error = models.IntegerField(default=0, null=True, blank=True)
    assist = models.IntegerField(default=0, null=True, blank=True)
    pitchStrike = models.IntegerField(default=0, null=True, blank=True)
    pitchBall = models.IntegerField(default=0, null=True, blank=True)
    totalBatterFaced = models.IntegerField(default=0, null=True, blank=0)
    totalInGameOut = models.IntegerField(default=0, blank=True, null=True) 
    oppHit = models.IntegerField(default=0, null=True, blank=True)
    oppRun = models.IntegerField(default=0, blank=True, null=True)
    earnedRun = models.IntegerField(default=0, blank=True, null=True)
    oppBaseOnBall = models.IntegerField(default=0, blank=True, null=True)
    oppStrikeOut = models.IntegerField(default=0, blank=True, null=True)
    hitBatter = models.IntegerField(default=0, blank=True, null=True)
    balk = models.IntegerField(default=0, blank=True, null=True)
    wildPitch = models.IntegerField(default=0, blank=True, null=True)
    oppHomeRun = models.IntegerField(default=0, blank=True, null=True)
    firstPitchStrike = models.IntegerField(default=0, blank=True, null=True)
    pickOff = models.IntegerField(default=0, blank=True, null=True)

    @property
    def atBat(self):
        return self.plateApperance - self.baseOnBall - self.hitByPitch - self.sacrificeFly - self.sacrificeBunt

    @property
    def hit(self):
        return self.single + self.double + self.triple + self.homeRun
    
    @property
    def battingAverage(self):
        if self.atBat == 0:
            return "-"
        return "{:.3f}".format(self.hit/self.atBat)
    
    @property
    def onBasePercentage(self):
        up = self.hit + self.baseOnBall + self.hitByPitch
        down = self.atBat + self.baseOnBall + self.hitByPitch + self.sacrificeFly
        if down == 0:
            return "-"
        return "{:.3f}".format(up/down)

    @property
    def sluggingPercentage(self):
        up = self.single + self.double*2 + self.triple*3 + self.homeRun*4
        down = self.atBat
        if down == 0:
            return "-"
        return "{:.3f}".format(up/down)

    @property
    def onBasePlusSlugging(self):
        if self.onBasePercentage == '-' and self.sluggingPercentage == '-':
            return '-'
        elif self.onBasePercentage == '-':
            return self.sluggingPercentage
        elif self.sluggingPercentage == '-':
            return self.onBasePercentage
        else:
            return self.sluggingPercentage + self.onBasePercentage
    
    @property
    def weightedOnBasePercentage(self):
        up = self.baseOnBall*0.69 + self.hitByPitch*0.72 + self.single*0.89 + self.double*1.27 + self.triple*1.62 + self.homeRun*2.1 
        down = self.atBat + self.baseOnBall + self.sacrificeFly + self.hitByPitch

        if down == 0:
            return '-'
        return "{:.3f}".format(up/down)
    
    @property
    def totalChance(self):
        return self.putOut + self.assist + self.error
    
    @property
    def fieldingPercentace(self):
        if self.totalChance == 0:
            return '-'
        up = self.putOut + self.assist
        return "{:.3f}".format(up/self.totalChance)
    
    @property
    def earnedRunAvarage(self):
        up = self.earnedRun*self.game.inningERA*3
        down = self.totalInGameOut
        if down == 0:
            if self.earnedRun != 0:
                return 'INF'
            else:
                return '-'
        return "{:.2f}".format(up/down)
    
    @property
    def walkAndHitPerInning(self):
        up = self.oppBaseOnBall + self.oppHit
        down = (self.totalInGameOut // 3) + ((self.totalInGameOut % 3) / 3)
        if self.totalInGameOut == 0:
            if up != 0:
                return 'INF'
            else:
                return '-'
        return "{:.1f}".format(up/down)
    
    @property
    def runnerAllowed(self):
        return self.oppHit + self.oppBaseOnBall + self.hitBatter
    
    # @property
    # def battingAvarageAgainst(self):
    #     up = self.oppHit
    #     down = self.totalBatterFaced - self.oppBaseOnBall - self.hitBatter - self.oppSacrificeFly - self.oppSacrificeBunt - self.catcherInterference
    #     if down == 0:
    #         return '-'
    #     return "{:.3f}".format(up/down)

    @property
    def firstPitchStrikePercenttage(self):
        if self.totalBatterFaced == 0:
            return '-'
        return "{:.3f}".format(self.firstPitchStrike/self.totalBatterFaced)
    
    @property
    def fieldingIndependentPitching(self):
        if self.totalInGameOut == 0:
            return '-'
        return ((self.oppHomeRun*13 + (self.hitBatter + self.oppBaseOnBall)*3 - self.oppStrikeOut*2) / ((self.totalInGameOut // 3) + ((self.totalInGameOut % 3) / 3))) + 3.2
    
    @property
    def pitchCount(self):
        return self.pitchStrike + self.pitchBall
   
class Transaction(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True,blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    
    type = models.IntegerField(
        choices=TRANSACTION_TYPE,
        blank=True,
        default=1,
    )
    description = models.TextField(blank=True, null=True)
    time = models.DateTimeField(default=datetime.datetime.now())
    price = models.BigIntegerField()

class Equipment(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True,blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.TextField(default="No name")
    category = models.IntegerField(
        choices=EQUIPMENT_TYPE,
        blank=True,
        null=True,
        default=-1,
    )
    brand = models.TextField(default="No brand")
    price = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to="equipments/", default="equipments/equipment.png", blank=True, null=True)
    avatar_str = models.TextField(blank=True, null=True)

class AtBat(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    teamScore =models.IntegerField(default=0, null=True, blank=True)
    oppScore = models.IntegerField(default=0, null=True, blank=True)
    out =  models.IntegerField(default=0, null=True, blank=True)
    inning =  models.IntegerField(default=1, null=True, blank=True)
    isTop = models.BooleanField(default=True, null=True, blank=True)
    ball =  models.IntegerField(default=0, null=True, blank=True)
    strike =  models.IntegerField(default=0, null=True, blank=True)
    isOffense =  models.IntegerField(default=0, null=True, blank=True)
    isRunnerFirstOff = models.ForeignKey(PlayerGame, on_delete=models.CASCADE, related_name='runner_first', null=True, blank=True)
    isRunnerSecondOff = models.ForeignKey(PlayerGame, on_delete=models.CASCADE, related_name='runner_second', null=True, blank=True)
    isRunnerThirdOff = models.ForeignKey(PlayerGame, on_delete=models.CASCADE, related_name='runner_third', null=True, blank=True)
    isRunnerFirstDef = models.IntegerField(null=True, blank=True)
    isRunnerSecondDef = models.IntegerField(null=True, blank=True)
    isRunnerThirdDef = models.IntegerField(null=True, blank=True)
    currentPlayer = models.IntegerField(null=True, blank=True, default=1)
    oppCurPlayer = models.IntegerField(null=True, blank=True, default=1)
    outcomeType =  models.IntegerField(
        choices=OUTCOME_TYPE,
        blank=True,
        null=True
    )
    description = models.TextField(blank=True, null=True)
    currentPitcher = models.ForeignKey(PlayerGame, on_delete=models.CASCADE, related_name='current_pitcher', null=True, blank=True)
    isLastState = models.BooleanField(default=False, null=True, blank=True)





