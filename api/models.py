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
    user_id = models.IntegerField(blank=True, null=True)


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

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, blank=True, null=True)
    location = models.TextField()
    timeStart = models.DateTimeField(default=datetime.datetime.now())
    timeEnd = models.DateTimeField()
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
        batter_games = BatterGame.objects.filter(game=self)
        if batter_games:
            team_scores = sum(batter_game.run for batter_game in batter_games)
            return team_scores
        return 0
    
    @property
    def team_error(self):
        fielder_games = FielderGame.objects.filter(game=self)
        if fielder_games:
            team_error = sum(fielder_game.error for fielder_game in fielder_games)
            return team_error
        return 0
    
    @property
    def team_hit(self):
        batter_games = BatterGame.objects.filter(game=self)
        if batter_games:
            team_hits = sum(batter_game.hit for batter_game in batter_games)
            return team_hits
        return 0
    
    @property
    def opp_score(self):
        pitcher_games = PitcherGame.objects.filter(game=self)
        if pitcher_games:
            opp_scores = sum(pitcher_game.oppRun for pitcher_game in pitcher_games)
            return opp_scores
        return 0
    
    @property
    def opp_error(self):
        batter_games = BatterGame.objects.filter(game=self)
        if batter_games:
            opp_error = sum(batter_game.onBaseByError for batter_game in batter_games)
            return opp_error
        return 0
    
    @property
    def opp_hit(self):
        pitcher_games = PitcherGame.objects.filter(game=self)
        if pitcher_games:
            opp_hits = sum(pitcher_game.oppHit for pitcher_game in pitcher_games)
            return opp_hits
        return 0

class BatterGame(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    plateApperance = models.IntegerField(default=0, null=True, blank=True)
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
    sacrificeHit = models.IntegerField(default=0, null=True, blank=True)
    stolenBase = models.IntegerField(default=0, null=True, blank=True)
    leftOnBase = models.IntegerField(default=0, null=True, blank=True)
    doublePlay = models.IntegerField(default=0, null=True, blank=True)
    run = models.IntegerField(default=0, null=True, blank=True)
    onBaseByError = models.IntegerField(default=0, null=True, blank=True)

    @property
    def atBat(self):
        return self.plateApperance - self.baseOnBall - self.hitByPitch - self.sacrificeFly - self.sacrificeHit

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
    
class FielderGame(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    currentPos = models.IntegerField(
        choices=POSITON,
        blank=True,
        default=-1,
    )
    playedPos = ArrayField(models.IntegerField(
        choices=POSITON,
        blank=True,
        default=-1,
    ))
    # totalChance = models.IntegerField(default=0)
    totalInGameOut = models.IntegerField(default=0, blank=True, null=True) 
    putOut = models.IntegerField(default=0, null=True, blank=True)
    assist = models.IntegerField(default=0, null=True, blank=True)
    error = models.IntegerField(default=0, null=True, blank=True)
    outfieldAssist = models.IntegerField(default=0, null=True, blank=True)

    @property
    def totalChance(self):
        return self.putOut + self.assist + self.error
    
    @property
    def fieldingPercentace(self):
        if self.totalChance == 0:
            return '-'
        up = self.putOut + self.assist
        return "{:.3f}".format(up/self.totalChance)
    
class PitcherGame(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    # pitchCount = models.IntegerField(default=0, null=True, blank=True)
    pitchBall = models.IntegerField(default=0, null=True, blank=True)
    pictchStrike = models.IntegerField(default=0, null=True, blank=True)
    totalBatterFaced = models.IntegerField(default=0, null=True, blank=0)
    totalInGameOut = models.IntegerField(default=0, blank=True, null=True) 
    oppHit = models.IntegerField(default=0, null=True, blank=True)
    oppRun = models.IntegerField(default=0, blank=True, null=True)
    earnedRun = models.IntegerField(default=0, blank=True, null=True)
    oppBaseOnBall = models.IntegerField(default=0, blank=True, null=True)
    strikeout = models.IntegerField(default=0, blank=True, null=True)
    hitBatter = models.IntegerField(default=0, blank=True, null=True)
    balk = models.IntegerField(default=0, blank=True, null=True)
    wildPitch = models.IntegerField(default=0, blank=True, null=True)
    oppHomeRun = models.IntegerField(default=0, blank=True, null=True)
    oppSacrificeHit = models.IntegerField(default=0, blank=True, null=True)
    oppSacrificeFly  = models.IntegerField(default=0, blank=True, null=True)
    catcherInterference = models.IntegerField(default=0, blank=True, null=True)
    firstPitchStrike = models.IntegerField(default=0, blank=True, null=True)
    pickOff = models.IntegerField(default=0, blank=True, null=True)

    @property
    def earnedRunAvarage(self):
        up = self.earnedRun*self.game.inningERA
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
    
    @property
    def battingAvarageAgainst(self):
        up = self.oppHit
        down = self.totalBatterFaced - self.oppBaseOnBall - self.hitBatter - self.oppSacrificeFly - self.oppSacrificeHit - self.catcherInterference
        if down == 0:
            return '-'
        return "{:.3f}".format(up/down)

    @property
    def firstPitchStrikePercenttage(self):
        if self.totalBatterFaced == 0:
            return '-'
        return "{:.3f}".format(self.firstPitchStrike/self.totalBatterFaced)
    
    @property
    def fieldingIndependentPitching(self):
        return ((self.oppHomeRun*13 + (self.hitBatter + self.oppBaseOnBall)*3 - self.strikeout*2) / ((self.totalInGameOut // 3) + ((self.totalInGameOut % 3) / 3))) + 3.2
    



