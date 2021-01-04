#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
import re
import os
import models
import argparse
import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from prettytable import PrettyTable

#
from api import (user_add, user_get, user_list, user_remove,
                 account_add, account_get, account_list, account_remove,
                 operation_add, operation_get, operation_list,
                 set_operation_tags,
                 #operation_remove,
                 transfer_add,
                 )


#
@contextmanager
def session_scope():
    session = Session()
    try:
        session.execute('set auto_increment_increment = 10')
        session.execute('set auto_increment_offset = 10')
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def import_operation(session, file):
    al = account_list(session=session, user_id='ed306e60-f42a-11e4-bd30-78e0f94055e9')
    account = {account.name: account.id for account in al}
    done_transfers = {}
    with open(file, 'r') as f:
        p = re.compile(r'^(?P<id>\d+)?;(?P<date>[^;]+)?;(?P<type>[^;]+)?;(?P<tag>[^;]+)?;(?P<desc>[^;]+)?;(?P<expenses>[^;]+)?;(?P<receipts>[^;]+)?;(?P<account>[^;]+)?\n')
        transfers = {}
        for line in f:
            m = p.match(line)
            if m:
                if float(m.group('expenses')) != 0:
                    amount = -float(m.group('expenses'))
                else:
                    amount = float(m.group('receipts'))
                if m.group('type') == 'Opening of account':
                    a = account_get(session=session, account_id=account[m.group('account')])
                    a.initial_balance = amount
                elif m.group('type') == 'Transfers':
                    key_1 = '{}-{}-{}-{}'.format(m.group('tag'), m.group('account'),
                                                 m.group('date'), abs(amount))
                    key_2 = '{}-{}-{}-{}'.format(m.group('account'), m.group('tag'),
                                                 m.group('date'), abs(amount))
                    if key_1 in transfers or key_2 in transfers:
                        continue
                    else:
                        transfers[key_1] = 1
                        transfers[key_2] = 1
                    operation_from = operation_add(session=session,
                            account_id=account[m.group('tag')],
                            amount=-amount,
                            description=m.group('desc'),
                            date=m.group('date'))
                    operation_to = operation_add(session=session,
                            account_id=account[m.group('account')],
                            amount=amount,
                            description=m.group('desc'),
                            date=m.group('date'))
                    transfer = transfer_add(session=session,
                            operation_from_id=operation_from.id,
                            operation_to_id=operation_to.id)
                    operation_from.transfer_id = transfer.id
                    operation_to.transfer_id = transfer.id
                else:
                    operation = operation_add(session=session,
                            account_id=account[m.group('account')],
                            amount=amount,
                            description=m.group('desc'),
                            date=m.group('date'))
                    set_operation_tags(session=session,
                            operation_id=operation.id,
                            tags=[m.group('type').lower(), m.group('tag').lower()])
                    
                #print m.group('date'), m.group('desc'), m.group('type'), m.group('tag'), amount
            else:
                print(line)


# main
if __name__ == '__main__':
    CONFIG_FILE = os.environ['APP_CFG']
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', help='environment to use', default='test')

    # argument parsing
    subparsers = parser.add_subparsers(
        dest='subparser', help='manage users, accounts, operations, etc.')
    #
    user_parser = subparsers.add_parser('user')
    #
    user_subparser = user_parser.add_subparsers(dest='subparser_user')
    user_add_parser = user_subparser.add_parser('add', help='add new user')
    user_add_parser.add_argument('--login', required=True)
    user_add_parser.add_argument('--password', required=True)
    user_add_parser.add_argument('--email', required=True)
    #
    user_get_parser = user_subparser.add_parser('get', help='get user')
    user_get_parser.add_argument('--login', required=True)
    #
    user_add_parser = user_subparser.add_parser('list', help='list users')
    #
    user_remove_parser = user_subparser.add_parser('remove',
                                                   help='remove user')
    user_remove_parser.add_argument('--login', required=True)
    #
    account_parser = subparsers.add_parser('account')
    #
    account_subparser = account_parser.add_subparsers(dest='subparser_account')
    account_add_parser = account_subparser.add_parser('add',
                                                      help='add new account')
    account_add_parser.add_argument('--owner', required=True)
    account_add_parser.add_argument('--name', required=True)
    account_add_parser.add_argument('--initial-balance', required=True)
    #
    account_get_parser = account_subparser.add_parser('get',
                                                      help='get account')
    account_get_parser.add_argument('--owner', required=True)
    account_get_parser.add_argument('--name', required=True)
    #
    account_remove_parser = account_subparser. \
        add_parser('remove', help='remove account')
    account_remove_parser.add_argument('--owner', required=True)
    account_remove_parser.add_argument('--name', required=True)
    #
    account_list_parser = account_subparser.add_parser('list',
                                                       help='list account')
    account_list_parser.add_argument('--owner')
    #
    operation_parser = subparsers.add_parser('operation')
    #
    operation_subparser = operation_parser.add_subparsers(dest='subparser_operation')
    operation_add_parser = operation_subparser.add_parser('add',
                                                      help='add new operation')
    operation_add_parser.add_argument('--owner', required=True)
    operation_add_parser.add_argument('--account', required=True)
    operation_add_parser.add_argument('--amount', required=True)
    operation_add_parser.add_argument('--type', required=True,
        choices=['expenses', 'receipts', 'transfers'])
    operation_add_parser.add_argument('--tags')
    #
    operation_get_parser = operation_subparser.add_parser('get',
                                                      help='get operation')
    operation_get_parser.add_argument('--owner', required=True)
    operation_get_parser.add_argument('--name', required=True)
    ### #
    ### operation_remove_parser = operation_subparser. \
    ###     add_parser('remove', help='remove operation')
    ### operation_remove_parser.add_argument('--owner', required=True)
    ### operation_remove_parser.add_argument('--name', required=True)
    #
    operation_import_parser = operation_subparser. \
        add_parser('import', help='import operation')
    operation_import_parser.add_argument('--file', required=True)
    #
    operation_list_parser = operation_subparser.add_parser('list',
                                                       help='list operation')
    operation_list_parser.add_argument('--owner')
    operation_list_parser.add_argument('--account')
    operation_list_parser.add_argument('--tags')

    #
    args = parser.parse_args()
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    DB_ENDPOINT = config.get(args.env, 'db_uri')

    # database engine
    engine = create_engine(DB_ENDPOINT, echo=False)
    Session = sessionmaker()
    Session.configure(bind=engine)

    # issuing wrapper functions based on made choices
    with session_scope() as session:
        if args.subparser == 'user':
            if args.subparser_user == 'add':
                print(user_add(session=session, login=args.login,
                               password=args.password, email=args.email))
            elif args.subparser_user == 'get':
                user = user_get(session=session, login=args.login)
                print('{}, {}, {}, {}'.format(user.uid, user.login,
                                              user.email, user.accounts))
            elif args.subparser_user == 'remove':
                print(user_remove(session=session, login=args.login))
            elif args.subparser_user == 'list':
                users = user_list(session=session)
                keys = ['user', 'email', 'cdate', 'mdate',
                        'active', 'accounts']
                table = PrettyTable(keys)
                for user in users:
                    table.add_row([str(user), user.email,
                        user.cdate, user.mdate or '--', user.active,
                        ', '.join(['{} ({})'.format(x.name, x.aid)
                                   for x in user.accounts])])
                print(table)
        elif args.subparser == 'account':
            if args.subparser_account == 'add':
                print(account_add(session=session, owner=args.owner,
                                  name=args.name,
                                  initial_balance=args.initial_balance))
            elif args.subparser_account == 'get':
                account = account_get(session=session, owner=args.owner,
                                      name=args.name)
                print('{}, {}, {}, {}'.format(account.aid, account.owner,
                                              account.name,
                                              account.initial_balance))
            elif args.subparser_account == 'remove':
                print(account_remove(session=session, owner=args.owner,
                                     name=args.name))
            elif args.subparser_account == 'list':
                accounts = account_list(session=session, owner=args.owner)
                if args.owner:
                    keys = ['account', 'initial balance']
                else:
                    keys = ['account', 'initial balance',
                            'owner']
                table = PrettyTable(keys)
                for account in accounts:
                    if args.owner:
                        table.add_row([str(account),
                            '{:0.2f}'.format(account.initial_balance)])
                    else:
                        table.add_row([str(account),
                            '{:0.2f}'.format(account.initial_balance),
                            str(account.owner)])
                print(table)
        elif args.subparser == 'operation':
            if args.subparser_operation == 'add':
                print(operation_add(session=session, owner=args.owner,
                    account=args.account, amount=args.amount,
                    type=args.type, tags=args.tags))
            elif args.subparser_operation == 'get':
                operation = operation_get(session=session, owner=args.owner,
                                      name=args.name)
                print('{}, {}, {}, {}'.format(operation.aid, operation.owner,
                                              operation.name,
                                              operation.initial_balance))
            ### elif args.subparser_operation == 'remove':
            ###     print operation_remove(session=session, owner=args.owner,
            ###                          name=args.name)
            elif args.subparser_operation == 'import':
                import_operation(session=session, file=args.file)
            elif args.subparser_operation == 'list':
                operations = operation_list(session=session, owner=args.owner,
                                            account=args.account,
                                            tags=args.tags.split(','))
                keys = ['operation', 'amount', 'date', 'order_by']
                #if not args.owner:
                keys.append('owner')
                #if not args.account:
                keys.append('account')
                keys.append('tags')
                table = PrettyTable(keys)
                for operation in operations:
                    values = [str(operation),
                              '{:0.2f}'.format(operation.amount),
                             operation.date, operation.order_by]
                    #if not args.owner:
                    values.append(operation.account.owner)
                    #if not args.account:
                    values.append(operation.account)
                    values.append(', '.join([x.tag.name
                                             for x in operation.tags]))
                    table.add_row(values)
                print(table)
