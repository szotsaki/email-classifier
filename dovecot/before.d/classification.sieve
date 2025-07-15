require ["enotify", "imap4flags", "variables", "vnd.dovecot.execute"];

# Change this to your postmaster address
set "error_notification_addr" "postmaster@example.com";

if anyof(header :is "X-Spam" "Yes",
         exists ["In-Reply-To", "References", "Original-Message-ID"])
{
    stop;
}

if execute :pipe :output "classification" "classifier.sh" {
    if string :is "${classification}" ["primary", "promotion", "social", "notification", "unsure", "error", "unknown"] {
        addflag "classification-${classification}";
    } else {
        notify :message "E-mail classification script returned with an unknown value: ${classification}" "mailto:${error_notification_addr}";
    }
} else {
    notify :message "E-mail classification script returned with an error" "mailto:${error_notification_addr}";
}