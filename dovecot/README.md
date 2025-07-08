# Dovecot setup

Dovecot configuration steps:

1. Enable virtual folders (e.g. Primary, Promotion) under INBOX.
2. Enable Sieve filtering of incoming messages.

## Set up the namespace

Copy the `dovecot/classification` directory to `/var/lib/dovecot/virtual` and modify `dovecot.conf` similarly to enable
the virtual folders.

This stores the virtual folder definitions (`dovecot-virtual` files) in a central location, whilst still enabling
user-specific indexing and subscriptions.

```wgetrc
namespace virtual-classification {
  prefix = "INBOX/"
  separator = /
  mail_driver = virtual
  mail_path = /var/lib/dovecot/virtual/classification
  mail_index_path = %{home}/index/virtual/classification

  # Store subscriptions file in parent namespace
  namespace_subscriptions = no

  mailbox Primary {
    auto = subscribe
  }
  mailbox Promotion {
    auto = subscribe
  }
  mailbox Social {
    auto = subscribe
  }
  mailbox Notification {
    auto = subscribe
  }
}
```

## Set up Sieve for incoming mails

Enable Sieve support for LMTP or LDA:

```wgetrc
protocol lmtp {
  mail_plugins {
    sieve = yes
  }
}
```

Copy the `before.d` and `extprograms` directories from `dovecot` into the global Sieve directory
`/var/lib/dovecot/sieve`.

Configure Sieve to enable processing of the `before.d` directory and running of external programs (only globally, not
for the user) from the `extprograms` directory.

```wgetrc
sieve_script before1 {
  type = before
  path = /var/lib/dovecot/sieve/before.d/
}
sieve_plugins {
  sieve_extprograms = yes
}
sieve_global_extensions {
  vnd.dovecot.execute = yes
}
sieve_execute_bin_dir = /var/lib/dovecot/sieve/extprograms
sieve_execute_exec_timeout = 150s
sieve_execute_input_eol = lf
```

Change the postmaster e-mail address in the header of `classification.sieve` to ensure that Sieve script errors are
reported.

```sieve
# Change this to your postmaster address
set "error_notification_addr" "postmaster@example.com";
```