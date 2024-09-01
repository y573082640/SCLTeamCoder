from scl_team_coder.util.antlr.antlr import syntax_check

file_path = '/root/SCLTeamCoder/scl_team_coder/util/antlr/input.scl'
with open(file_path,'r') as fp:
    error, success = syntax_check(fp.read())
    print(error, success)