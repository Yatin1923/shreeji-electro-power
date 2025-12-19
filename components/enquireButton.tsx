import React, { useState } from "react";
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  CircularProgress,
  Snackbar,
  Alert,
} from "@mui/material";
import { MuiTelInput, matchIsValidTel } from "mui-tel-input";
import { finalization } from "process";

type EnquireButtonProps = {
  productName?: string;
};

const EnquireButton: React.FC<EnquireButtonProps> = ({ productName }) => {
  const [open, setOpen] = useState(false);
  const [showToastr, setShowToastr] = useState(false);
  const [loading, setLoading] = useState(false);
  const [phoneError, setPhoneError] = useState(false);

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    source: "",
    quantity: 1,
    message: "",
  });

  const FORM_EMAIL = "inquiry@shreejielectropower.com";

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (phoneError) return;

    setLoading(true);
    const pageUrl = window.location.href;

    try {
      const res = await fetch(`https://formsubmit.co/ajax/${FORM_EMAIL}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          phone: form.phone,
          source: form.source,
          quantity: form.quantity,
          message: form.message,
          product_name: productName ?? "N/A",
          page_url: pageUrl,
        }),
      });

      const data = await res.json();

      if (data.success === "true") {
        setShowToastr(true);
        setForm({
          name: "",
          email: "",
          phone: "",
          source: "",
          quantity: 1,
          message: "",
        });
      }
    } catch (err) {
      // setShowToastr(true);
      console.error("FormSubmit Error:", err);
    }finally{
      setOpen(false);
    }

    setLoading(false);
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        className="!normal-case mt-2"
        onClick={() => setOpen(true)}
      >
        Enquire now!
      </Button>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle sx={{ lineHeight: 1.3 }}>
          Enquire about:
          <div className="font-bold text-sky-600 break-words">
            {productName}
          </div>
        </DialogTitle>

        <DialogContent>
          <form
            className="flex flex-col gap-6 p-2 sm:p-2"
            onSubmit={handleSubmit}
          >
            <TextField
              label="Full name"
              name="name"
              fullWidth
              required
              value={form.name}
              onChange={handleChange}
            />

            <TextField
              label="Email"
              name="email"
              type="email"
              fullWidth
              required
              value={form.email}
              onChange={handleChange}
              error={!!form.email && !/^\S+@\S+\.\S+$/.test(form.email)}
              helperText={
                !!form.email && !/^\S+@\S+\.\S+$/.test(form.email)
                  ? "Enter a valid email"
                  : ""
              }
            />

            <MuiTelInput
              label="Phone number"
              fullWidth
              defaultCountry="IN"
              forceCallingCode
              value={form.phone}
              onChange={(value) => {
                setForm({ ...form, phone: value });
                setPhoneError(!matchIsValidTel(value));
              }}
              error={phoneError}
              helperText={
                phoneError ? "Please enter a valid phone number" : ""
              }
              required
            />

            <TextField
              label="Quantity"
              name="quantity"
              type="number"
              fullWidth
              required
              inputProps={{ min: 1 }}
              value={form.quantity}
              onChange={handleChange}
            />

            <TextField
              label="Message"
              name="message"
              fullWidth
              multiline
              minRows={3}
              value={form.message}
              onChange={handleChange}
            />

            <TextField
              label="How did you find us?"
              name="source"
              fullWidth
              value={form.source}
              onChange={handleChange}
            />

            <div className="sticky bottom-0 bg-white dark:bg-neutral-900 py-3">
              <Button
                type="submit"
                variant="contained"
                size="large"
                className="!bg-sky-600 hover:!bg-sky-700 !normal-case"
                fullWidth
                disabled={loading || phoneError}
              >
                {loading ? (
                  <CircularProgress size={26} color="inherit" />
                ) : (
                  "Send"
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <Snackbar
        open={showToastr}
        autoHideDuration={3000}
        onClose={() => setShowToastr(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          severity="success"
          variant="filled"
          onClose={() => setShowToastr(false)}
        >
          Message sent successfully!
        </Alert>
      </Snackbar>
    </>
  );
};

export default EnquireButton;
